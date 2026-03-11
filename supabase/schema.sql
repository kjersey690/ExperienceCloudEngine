create table deployment_errors_queue (
  id uuid default gen_random_uuid() primary key,
  created_at timestamptz default now(),
  error_name text not null,
  replication_steps text,
  resolution_steps text,
  category text,
  status text default 'Pending Review' -- Options: Pending, Approved, Rejected
);