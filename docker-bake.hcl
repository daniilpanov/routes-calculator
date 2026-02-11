variable "TAG" {
  default = "latest"
}

group "default" {
  targets = ["python-apps", "reverseproxy"]
}

target "python-apps" {
  context = "."
  dockerfile = "Dockerfile"
  target = "python-apps"
  tags = ["danielgreen1806/calculator-python-apps:${TAG}"]
}

target "frontadmin-builder" {
  context = "."
  dockerfile = "Dockerfile"
  target = "frontadmin-builder"
}

target "reverseproxy" {
  context = "."
  dockerfile = "Dockerfile"
  target = "reverseproxy"
  tags = ["danielgreen1806/calculator-reverseproxy:${TAG}"]
  contexts = {
    frontadmin-builder = "target:frontadmin-builder"
  }
}
