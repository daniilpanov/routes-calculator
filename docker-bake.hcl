variable "TAG" {
  default = "latest"
}

group "default" {
  targets = ["backend", "auth", "reverseproxy"]
}

target "backend" {
  context = "."
  dockerfile = "deploy.Dockerfile"
  target = "backend"
  tags = ["danielgreen1806/calculator-backend:${TAG}"]
}

target "auth" {
  context = "."
  dockerfile = "deploy.Dockerfile"
  target = "auth"
  tags = ["danielgreen1806/auth-backend:${TAG}"]
}

target "frontadmin" {
  context = "."
  dockerfile = "deploy.Dockerfile"
  target = "frontadmin"
}

target "reverseproxy" {
  context = "."
  dockerfile = "deploy.Dockerfile"
  target = "reverseproxy"
  tags = ["danielgreen1806/calculator-reverseproxy:${TAG}"]
  contexts = {
    frontadmin = "target:frontadmin"
  }
}