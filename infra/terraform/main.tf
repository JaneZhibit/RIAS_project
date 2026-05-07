# IaC sample: S3-compatible object storage (MinIO) on Docker.
# Use alternate host ports so this does not clash with docker-compose MinIO (9000/9001).
# Primary local stack: root docker-compose.yml — apply this only when compose MinIO is stopped
# or change external ports further.

resource "docker_network" "rias" {
  name = "rias_tf_net"
}

resource "docker_volume" "minio_data" {
  name = "rias_tf_minio_data"
}

resource "docker_container" "minio" {
  name  = "rias-tf-minio"
  image = "minio/minio:latest"

  restart = "unless-stopped"

  command = ["server", "/data", "--console-address", ":9001"]

  env = [
    "MINIO_ROOT_USER=minioadmin",
    "MINIO_ROOT_PASSWORD=minioadmin",
  ]

  networks_advanced {
    name = docker_network.rias.name
  }

  mounts {
    type   = "volume"
    target = "/data"
    source = docker_volume.minio_data.name
  }

  ports {
    internal = 9000
    external = 19005
  }

  ports {
    internal = 9001
    external = 19006
  }
}
