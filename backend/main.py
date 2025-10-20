# 重要：必须在导入ultralytics之前修复PyTorch
import torch
import os
import sys

print("[INFO] 正在初始化PyTorch兼容性补丁...")

# 方法1: 设置环境变量（在任何导入之前）
os.environ['TORCH_FORCE_WEIGHTS_ONLY_LOAD'] = '0'

# 方法2: Monkey patch torch.load
_original_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    # 强制设置weights_only=False
    kwargs['weights_only'] = False
    return _original_torch_load(*args, **kwargs)

torch.load = _patched_torch_load
print(f"[INFO] PyTorch版本: {torch.__version__}")
print("[INFO] 已应用PyTorch兼容性补丁 (weights_only=False)")

# 现在才导入其他模块
from fastapi import FastAPI, File, UploadFile, Form, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import cv2
import json
import time
from pathlib import Path
import shutil
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client

# 最后导入ultralytics
from ultralytics import YOLO
print("[INFO] Ultralytics导入成功")

# 方法3: 添加安全全局变量（额外保险）
try:
    import ultralytics.nn.tasks
    torch.serialization.add_safe_globals([ultralytics.nn.tasks.DetectionModel])
    print("[INFO] 已添加ultralytics到PyTorch安全列表")
except Exception as e:
    print(f"[WARNING] 添加安全列表失败: {e}")

# 加载环境变量
load_dotenv()

# 初始化Supabase客户端
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

# 调试输出
print(f"[DEBUG] SUPABASE_URL: {supabase_url}")
if supabase_key:
    print(f"[DEBUG] SUPABASE_KEY 长度: {len(supabase_key)} 字符")
    print(f"[DEBUG] SUPABASE_KEY 前20个字符: {supabase_key[:20]}...")
else:
    print("[DEBUG] SUPABASE_KEY 未设置")

supabase: Optional[Client] = None
if supabase_url and supabase_key:
    try:
        supabase = create_client(supabase_url, supabase_key)
        print("[INFO] Supabase客户端初始化成功")
    except Exception as e:
        print(f"[WARNING] Supabase客户端初始化失败: {e}")
        import traceback
        traceback.print_exc()
else:
    print("[WARNING] 未配置 Supabase 环境变量，文件上传功能将被禁用")

app = FastAPI(title="YOLOv8 Detection API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建必要的目录
UPLOAD_DIR = Path("uploads")
MODEL_DIR = Path("models")
RESULT_DIR = Path("results")

for directory in [UPLOAD_DIR, MODEL_DIR, RESULT_DIR]:
    directory.mkdir(exist_ok=True)

# 存储每个用户的模型
user_models = {}

@app.get("/")
async def root():
    return {
        "message": "YOLOv8 Detection API",
        "version": "1.0.0",
        "endpoints": {
            "upload_model": "/api/upload-model",
            "detect": "/api/detect"
        }
    }

@app.post("/api/upload-model")
async def upload_model(
    model: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    """
    上传YOLOv8模型权重文件
    """
    try:
        # 从Authorization头部获取用户ID
        user_id = authorization.replace("Bearer ", "") if authorization else "default"
        
        # 验证文件格式
        if not (model.filename.endswith('.pt') or model.filename.endswith('.pth')):
            raise HTTPException(status_code=400, detail="只支持.pt和.pth格式的模型文件")
        
        # 保存模型文件
        model_path = MODEL_DIR / f"{user_id}_{model.filename}"
        
        with open(model_path, "wb") as buffer:
            shutil.copyfileobj(model.file, buffer)
        
        # 加载模型以验证其有效性
        try:
            print(f"[INFO] 正在验证模型: {model_path}")
            
            # 使用兼容模式加载（已通过全局patch设置）
            yolo_model = YOLO(str(model_path))
            
            user_models[user_id] = str(model_path)
            print(f"[SUCCESS] 模型验证成功: {model.filename}")
        except Exception as e:
            # 如果模型无效，删除文件
            print(f"[ERROR] 模型验证失败: {str(e)}")
            if model_path.exists():
                model_path.unlink()
            
            # 提供更友好的错误信息
            error_msg = str(e)
            if 'weights_only' in error_msg or 'WeightsUnpickler' in error_msg:
                error_msg = "模型文件格式不兼容。这可能是PyTorch版本问题，建议使用PyTorch 2.5或更早版本，或使用最新版本的ultralytics训练的模型。"
            
            raise HTTPException(status_code=400, detail=f"无效的模型文件: {error_msg}")
        
        return {
            "success": True,
            "message": "模型上传成功",
            "model_path": str(model_path),
            "user_id": user_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

def upload_file_to_supabase(file_path: Path, user_id: str, file_type: str, is_result: bool = False) -> Optional[str]:
    """
    上传文件到Supabase存储桶
    
    Args:
        file_path: 本地文件路径
        user_id: 用户ID
        file_type: 文件类型 ('image' 或 'video')
        is_result: 是否为结果文件
    
    Returns:
        公共URL或None（如果上传失败）
    """
    if not supabase:
        print("[WARNING] Supabase未配置，跳过文件上传")
        return None
    
    try:
        # 读取文件内容
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # 构造存储路径
        folder = 'results' if is_result else 'original'
        file_extension = file_path.suffix
        storage_path = f"{user_id}/{file_type}s/{folder}/{int(time.time())}{file_extension}"
        
        print(f"[INFO] 正在上传文件到Supabase: {storage_path}")
        
        # 上传到Supabase
        response = supabase.storage.from_('detection-files').upload(
            path=storage_path,
            file=file_content,
            file_options={"content-type": f"image/jpeg" if file_extension.lower() in ['.jpg', '.jpeg'] else f"video/mp4"}
        )
        
        # 获取公共URL
        public_url_response = supabase.storage.from_('detection-files').get_public_url(storage_path)
        public_url = public_url_response
        
        print(f"[INFO] 文件上传成功: {public_url}")
        return public_url
        
    except Exception as e:
        print(f"[ERROR] 上传文件到Supabase失败: {e}")
        return None

def save_detection_to_database(user_id: str, file_type: str, original_url: str, result_url: str, detections: list, params: dict) -> Optional[dict]:
    """
    保存检测记录到数据库
    
    Returns:
        数据库记录或None（如果保存失败）
    """
    if not supabase:
        print("[WARNING] Supabase未配置，跳过数据库保存")
        return None
    
    try:
        print("[INFO] 正在保存检测记录到数据库...")
        
        data = {
            'user_id': user_id,
            'file_type': file_type,
            'original_file': original_url,
            'result_file': result_url,
            'detections': detections,
            'params': params
        }
        
        response = supabase.table('detection_history').insert(data).execute()
        
        print("[INFO] 检测记录保存成功")
        return response.data[0] if response.data else None
        
    except Exception as e:
        print(f"[ERROR] 保存检测记录失败: {e}")
        return None

@app.post("/api/detect")
async def detect(
    file: UploadFile = File(...),
    type: str = Form(...),
    params: str = Form(...),
    authorization: Optional[str] = Header(None)
):
    """
    执行YOLOv8检测
    参数:
    - file: 图片或视频文件
    - type: 'image' 或 'video'
    - params: JSON格式的检测参数
    """
    try:
        print("\n[INFO] ==========  开始检测  ==========")
        # 获取用户ID
        user_id = authorization.replace("Bearer ", "") if authorization else "default"
        print(f"[INFO] 用户ID: {user_id}")
        print(f"[INFO] 文件类型: {type}")
        print(f"[INFO] 文件名: {file.filename}")
        
        # 检查用户是否已上传模型
        if user_id not in user_models:
            print(f"[ERROR] 用户 {user_id} 未上传模型")
            print(f"[INFO] 已上传模型的用户: {list(user_models.keys())}")
            raise HTTPException(status_code=400, detail="请先上传模型文件")
        
        # 解析参数并确保类型正确
        detection_params = json.loads(params)
        img_size = int(detection_params.get('imgSize', 640))
        confidence = float(detection_params.get('confidence', 0.25))
        iou_threshold = float(detection_params.get('iouThreshold', 0.45))
        max_det = int(detection_params.get('maxDetections', 300))
        frame_skip = int(detection_params.get('frameSkip', 1))  # 视频帧间隔，1表示每帧都检测（默认）
        
        # 保存上传的文件
        file_extension = os.path.splitext(file.filename)[1]
        input_path = UPLOAD_DIR / f"{user_id}_{int(time.time())}{file_extension}"
        
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 加载模型
        print(f"[INFO] 正在加载模型: {user_models[user_id]}")
        try:
            model = YOLO(user_models[user_id])
            print("[INFO] 模型加载成功")
        except Exception as model_error:
            print(f"[ERROR] 模型加载失败: {model_error}")
            raise HTTPException(status_code=500, detail=f"模型加载失败: {str(model_error)}")
        
        start_time = time.time()
        
        print(f"[INFO] ========== 开始{type}检测 ==========")
        print(f"[INFO] 检测参数: size={img_size}, conf={confidence}, iou={iou_threshold}, max_det={max_det}")
        
        if type == 'image':
            # 处理图片
            print(f"[INFO] 处理图片文件...")
            try:
                results = model.predict(
                    source=str(input_path),
                    imgsz=img_size,
                    conf=confidence,
                    iou=iou_threshold,
                    max_det=max_det,
                    save=False,
                    verbose=False
                )
                print(f"[INFO] 检测完成, 检测到 {len(results[0].boxes)} 个目标")
            except Exception as predict_error:
                print(f"[ERROR] 检测失败: {predict_error}")
                import traceback
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=f"检测失败: {str(predict_error)}")
            
            # 绘制检测结果
            try:
                result_image = results[0].plot()
                print("[INFO] 绘制结果成功")
            except Exception as plot_error:
                print(f"[ERROR] 绘制结果失败: {plot_error}")
                raise HTTPException(status_code=500, detail=f"绘制结果失败: {str(plot_error)}")
            
            # 保存结果
            result_filename = f"result_{user_id}_{int(time.time())}.jpg"
            result_path = RESULT_DIR / result_filename
            try:
                cv2.imwrite(str(result_path), result_image)
                print(f"[INFO] 结果已保存: {result_path}")
            except Exception as save_error:
                print(f"[ERROR] 保存结果失败: {save_error}")
                raise HTTPException(status_code=500, detail=f"保存结果失败: {str(save_error)}")
            
            # 提取检测信息
            detections = []
            for box in results[0].boxes:
                detections.append({
                    'class': results[0].names[int(box.cls[0])],
                    'confidence': float(box.conf[0]),
                    'bbox': box.xyxy[0].tolist()
                })
        
        else:  # video
            # 处理视频
            print(f"[INFO] 处理视频文件: {input_path}")
            cap = cv2.VideoCapture(str(input_path))
            
            # 验证视频是否成功打开
            if not cap.isOpened():
                print(f"[ERROR] 无法打开视频文件: {input_path}")
                raise HTTPException(status_code=400, detail="无法读取视频文件，请检查文件格式")
            
            # 获取视频信息
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            print(f"[INFO] 视频信息: FPS={fps}, 尺寸={width}x{height}, 总帧数={total_frames}")
            
            if fps == 0 or width == 0 or height == 0:
                print(f"[ERROR] 视频信息无效: FPS={fps}, 尺寸={width}x{height}")
                cap.release()
                raise HTTPException(status_code=400, detail="视频文件损坏或格式不支持")
            
            # 创建输出视频
            result_filename = f"result_{user_id}_{int(time.time())}.mp4"
            result_path = RESULT_DIR / result_filename
            
            # 尝试多种编码器，优先使用H264
            fourcc_options = [
                ('avc1', 'H264'),  # H.264编码（最兼容）
                ('H264', 'H264'),  # 备选H264
                ('XVID', 'XVID'),  # Xvid编码
                ('MJPG', 'MJPEG'), # Motion JPEG
                ('mp4v', 'MPEG-4') # 最后的备选
            ]
            
            out = None
            used_codec = None
            
            for codec_code, codec_name in fourcc_options:
                try:
                    fourcc = cv2.VideoWriter_fourcc(*codec_code)
                    test_out = cv2.VideoWriter(str(result_path), fourcc, fps, (width, height))
                    
                    if test_out.isOpened():
                        out = test_out
                        used_codec = codec_name
                        print(f"[INFO] 使用视频编码器: {codec_name} ({codec_code})")
                        break
                    else:
                        test_out.release()
                except Exception as e:
                    print(f"[WARNING] 编码器 {codec_name} 不可用: {e}")
                    continue
            
            if out is None or not out.isOpened():
                cap.release()
                raise HTTPException(status_code=500, detail="无法创建视频输出文件，请检查OpenCV和编码器配置")
            
            detections = []
            frame_count = 0
            total_detections = 0
            
            print(f"[INFO] 开始逐帧处理视频...")
            print(f"[INFO] 帧间隔设置: {frame_skip} (1=每帧检测, 2-5=每 N帧检测)")
            
            # 如果frame_skip>1，提示用户可能会有跳跃感
            if frame_skip > 1:
                print(f"[WARNING] 帧间隔 > 1 可能导致检测框跳跃，建议设置 frameSkip=1 获得流畅效果")
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 根据frameSkip参数决定处理频率
                if frame_count % frame_skip == 0:
                    # 进行检测
                    results = model.predict(
                        source=frame,
                        imgsz=img_size,
                        conf=confidence,
                        iou=iou_threshold,
                        max_det=max_det,
                        save=False,
                        verbose=False
                    )
                    
                    # 绘制检测结果
                    annotated_frame = results[0].plot()
                    
                    # 收集检测信息
                    for box in results[0].boxes:
                        detections.append({
                            'class': results[0].names[int(box.cls[0])],
                            'confidence': float(box.conf[0]),
                            'bbox': box.xyxy[0].tolist(),
                            'frame': frame_count
                        })
                    
                    # 统计检测数量
                    current_detections = len(results[0].boxes)
                    total_detections += current_detections
                    
                    # 进度输出
                    if frame_count % 50 == 0:
                        print(f"[INFO] 已处理 {frame_count} 帧, 当前帧检测到 {current_detections} 个目标")
                else:
                    # 不检测的帧，直接使用原始帧（不显示过时的检测框）
                    annotated_frame = frame
                
                # 写入输出视频
                out.write(annotated_frame)
                frame_count += 1
            
            cap.release()
            out.release()
            
            # 验证输出视频文件
            if not result_path.exists():
                raise HTTPException(status_code=500, detail="视频输出文件创建失败")
            
            file_size = result_path.stat().st_size
            if file_size == 0:
                raise HTTPException(status_code=500, detail="视频输出文件为空")
            
            # 尝试打开输出视频验证其有效性
            verify_cap = cv2.VideoCapture(str(result_path))
            if not verify_cap.isOpened():
                verify_cap.release()
                print(f"[ERROR] 输出视频无法打开，文件可能损坏")
                raise HTTPException(status_code=500, detail="生成的视频文件无效，请尝试其他编码器")
            
            verify_frame_count = int(verify_cap.get(cv2.CAP_PROP_FRAME_COUNT))
            verify_cap.release()
            
            print(f"[INFO] 视频处理完成:")
            print(f"[INFO] - 总帧数: {frame_count}")
            print(f"[INFO] - 输出视频帧数: {verify_frame_count}")
            print(f"[INFO] - 处理帧数: {frame_count // frame_skip}")
            print(f"[INFO] - 帧间隔: {frame_skip} (1=每帧检测, 5=每5帧检测)")
            print(f"[INFO] - 总检测数: {total_detections}")
            print(f"[INFO] - 唯一检测结果: {len(detections)}")
            print(f"[INFO] - 文件大小: {file_size / 1024 / 1024:.2f} MB")
            print(f"[INFO] - 编码器: {used_codec}")
            
            # 使用FFmpeg重新编码以提高播放流畅度
            try:
                import subprocess
                print(f"[INFO] 尝试使用FFmpeg优化视频...")
                
                temp_path = result_path.with_suffix('.temp.mp4')
                
                # FFmpeg命令：重新编码为H.264，优化流畅度
                cmd = [
                    'ffmpeg',
                    '-i', str(result_path),
                    '-c:v', 'libx264',        # H.264编码
                    '-preset', 'fast',        # 快速编码
                    '-crf', '23',             # 质量（18-28）
                    '-pix_fmt', 'yuv420p',    # 兼容性最好
                    '-movflags', '+faststart', # 优化网络播放
                    '-y',                     # 覆盖
                    str(temp_path)
                ]
                
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=300,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )
                
                if result.returncode == 0 and temp_path.exists():
                    # 替换原文件
                    result_path.unlink()
                    temp_path.rename(result_path)
                    
                    new_size = result_path.stat().st_size
                    print(f"[INFO] ✓ FFmpeg优化成功")
                    print(f"[INFO] - 优化后大小: {new_size / 1024 / 1024:.2f} MB")
                    print(f"[INFO] - 视频将更加流畅")
                else:
                    print(f"[WARNING] FFmpeg优化失败，使用原始视频")
                    if temp_path.exists():
                        temp_path.unlink()
                        
            except FileNotFoundError:
                print(f"[INFO] FFmpeg未安装，跳过优化（视频可能不够流畅）")
                print(f"[INFO] 提示: 安装FFmpeg可以获得更流畅的视频播放")
            except subprocess.TimeoutExpired:
                print(f"[WARNING] FFmpeg优化超时，使用原始视频")
            except Exception as e:
                print(f"[WARNING] FFmpeg优化出错: {e}，使用原始视频")
        
        process_time = time.time() - start_time
        
        print(f"[INFO] ========== 检测完成 ==========")
        print(f"[INFO] 检测结果数量: {len(detections)}")
        print(f"[INFO] 处理时间: {process_time:.2f}秒")
        
        # 上传原始文件和结果文件到Supabase
        original_url = None
        result_url_supabase = None
        
        if supabase:
            print("[INFO] 开始上传文件到Supabase存储桶...")
            
            # 上传原始文件
            original_url = upload_file_to_supabase(input_path, user_id, type, is_result=False)
            
            # 上传结果文件
            result_url_supabase = upload_file_to_supabase(result_path, user_id, type, is_result=True)
            
            # 保存到数据库
            if original_url and result_url_supabase:
                save_detection_to_database(
                    user_id=user_id,
                    file_type=type,
                    original_url=original_url,
                    result_url=result_url_supabase,
                    detections=detections,
                    params=detection_params
                )
        
        # 清理输入文件
        if input_path.exists():
            input_path.unlink()
        
        return {
            "success": True,
            "resultUrl": f"/api/results/{result_filename}",
            "originalUrlSupabase": original_url,
            "resultUrlSupabase": result_url_supabase,
            "detections": detections,
            "processTime": process_time,
            "params": detection_params
        }
    
    except HTTPException:
        raise
    except Exception as e:
        # 清理文件
        print(f"[ERROR] 未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        if 'input_path' in locals() and input_path.exists():
            input_path.unlink()
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")

@app.get("/api/results/{filename}")
async def get_result(filename: str):
    """
    获取结果文件
    """
    file_path = RESULT_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(file_path)

@app.delete("/api/cleanup/{user_id}")
async def cleanup(user_id: str):
    """
    清理用户的临时文件
    """
    try:
        # 删除用户的模型
        if user_id in user_models:
            model_path = Path(user_models[user_id])
            if model_path.exists():
                model_path.unlink()
            del user_models[user_id]
        
        # 删除用户的上传文件和结果文件
        for directory in [UPLOAD_DIR, RESULT_DIR]:
            for file_path in directory.glob(f"{user_id}_*"):
                file_path.unlink()
        
        return {"success": True, "message": "清理完成"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清理失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
