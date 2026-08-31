variable "IMAGE_NAME" {
  default = "tecnativa/docker-socket-proxy"
}
variable "VERSIONS" {
  default = ["3.0", "3.2", "3.4"]
}
variable "SUFFIX" {
 default = "latest"
}


group "default" {
  targets = [
    "latest",
  ]
}
variable "HAPROXY_VERSION" {
    default = replace(VERSIONS[length(VERSIONS) - 1],".","_")
}
variable "PLATFORMS" {
    default = ""
}
group "all" {
  targets = flatten([
    for version in VERSIONS : [
      replace(version,".","_")
    ]
  ])
}
target "latest" {
    tags = [
        "${IMAGE_NAME}:${SUFFIX}"
    ]
    context = "."
    dockerfile = "Dockerfile"
    platforms = split(",", PLATFORMS)
    args = {
    "HAPROXY_VERSION" = "lts"
  }
}
target "socket_proxy" {
  matrix = {
    version = VERSIONS
  }
  name = replace(version, ".","_")
  tags = [
    "${IMAGE_NAME}:${version}${SUFFIX}"
  ]
  context = "."
  dockerfile = "Dockerfile"
  platforms = split(",", PLATFORMS)
  args = {
    "HAPROXY_VERSION" = version
  }
}
