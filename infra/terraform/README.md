# Terraform (Docker provider) — MinIO sample

Провайдер: `kreuzwerker/docker`. Создаёт сеть, том и контейнер MinIO на портах **19005** (S3 API) и **19006** (консоль), чтобы не пересекаться с `docker-compose` (9000/9001).

```bash
terraform init
terraform apply
```

Перед `apply` останови Compose-MinIO, если нужны те же порты, или поменяй `external` в `main.tf`.
