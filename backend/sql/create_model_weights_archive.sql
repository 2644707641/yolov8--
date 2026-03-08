-- 创建模型权重归档表：用于“可恢复删除”。
-- 执行方式：在 Supabase SQL Editor 执行本文件内容。

create extension if not exists pgcrypto;

create table if not exists public.model_weights_archive (
    archive_id uuid primary key default gen_random_uuid(),
    original_weight_id text not null,
    user_id text not null,
    name text not null,
    file_path text not null,
    file_size bigint not null default 0,
    description text,
    original_created_at timestamptz,
    was_active boolean not null default false,
    deleted_at timestamptz not null default now(),
    deleted_by text not null,
    is_restored boolean not null default false,
    restored_at timestamptz,
    restored_by text
);

create index if not exists idx_model_weights_archive_user_id
    on public.model_weights_archive(user_id);

create index if not exists idx_model_weights_archive_deleted_at
    on public.model_weights_archive(deleted_at desc);

create index if not exists idx_model_weights_archive_is_restored
    on public.model_weights_archive(is_restored);
