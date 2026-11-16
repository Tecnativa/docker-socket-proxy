variable "IMAGE_NAME" {
  default = "tecnativa/docker-socket-proxy"
}

variable "VERSIONS" {
  type    = list(string)
  default = ["lts", "3.4"]
}

# This version also gets the "latest" tag
variable "LATEST_VERSION" {
  default = "lts"
}

# Optional suffix appended to every tag
variable "TAG_SUFFIX" {
  default = ""
}

# Comma-separated, e.g. "linux/amd64,linux/arm64". Empty = native platform only.
variable "PLATFORMS" {
  default = ""
}
variable "ATTEST" {
  type    = bool
  default = false
}

group "default" {
  targets = ["all"]
}

group "all" {
  targets = [for version in VERSIONS : replace(version, ".", "_")]
}
# USed in ci to add labels automatically
target "docker-metadata-action" {}

target "socket_proxy" {
  inherits = ["docker-metadata-action"]
  matrix = {
    version = VERSIONS
  }
  # Target names can't contain dots: 3.4 -> 3_4
  name       = replace(version, ".", "_")
  context    = "."
  dockerfile = "Dockerfile"
  platforms  = split(",", PLATFORMS)
  args = {
    HAPROXY_VERSION = version
  }
  tags = concat(
    ["${IMAGE_NAME}:${version}${TAG_SUFFIX}"],
    version == LATEST_VERSION ? ["${IMAGE_NAME}:latest${TAG_SUFFIX}"] : []
  )
  attest = ATTEST ? ["type=sbom", "type=provenance,mode=max"] : []
}
