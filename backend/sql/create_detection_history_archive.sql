-- 创建历史记录归档表：用于“可恢复删除”。
-- 执行方式：在 Supabase SQL Editor 执行本文件内容。

create extension if not exists pgcrypto;

create table if not exists public.detection_history_archive (
    archive_id uuid primary key default gen_random_uuid(),
    original_history_id text not null,
    user_id text not null,
    file_type text not null,
    original_file text,
    result_file text,
    detections jsonb,
    params jsonb,
    original_created_at timestamptz,
    deleted_at timestamptz not null default now(),
    deleted_by text not null,
    is_restored boolean not null default false,
    restored_at timestamptz,
    restored_by text
);

create index if not exists idx_detection_history_archive_user_id
    on public.detection_history_archive(user_id);

create index if not exists idx_detection_history_archive_deleted_at
    on public.detection_history_archive(deleted_at desc);

create index if not exists idx_detection_history_archive_is_restored
    on public.detection_history_archive(is_restored);
