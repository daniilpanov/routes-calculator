variable "TAG" {
  default = "latest"
}

group "default" {
  targets = ["python-apps", "reverseproxy"]
}

target "python-apps" {
  context = "."
  dockerfile = "deploy.Dockerfile"
  target = "python-apps"
  tags = ["danielgreen1806/calculator-python-apps:${TAG}"]
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
