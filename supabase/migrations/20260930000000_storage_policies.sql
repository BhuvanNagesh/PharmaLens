create policy "pharmalens anon upload"
on storage.objects
for insert
to anon
with check (bucket_id = 'pharmalens-docs');

create policy "pharmalens anon read"
on storage.objects
for select
to anon
using (bucket_id = 'pharmalens-docs');

create policy "pharmalens anon delete"
on storage.objects
for delete
to anon
using (bucket_id = 'pharmalens-docs');
