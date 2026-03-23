variable "TAG" {
  default = "latest"
}

group "default" {
  targets = ["python-apps", "db-migration", "reverseproxy"]
}

target "python-apps" {
  context = "."
  dockerfile = "Dockerfile"
  target = "python-apps"
  tags = ["danielgreen1806/calculator-python-apps:${TAG}"]
}

target "db-migration" {
  context = "."
  dockerfile = "Dockerfile"
  target = "db-migration"
  tags = ["danielgreen1806/calculator-db-migration:${TAG}"]
}

target "frontend-builder" {
  context = "."
  dockerfile = "Dockerfile"
  target = "frontend-builder"
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
    frontend-builder = "target:frontend-builder",
    frontadmin-builder = "target:frontadmin-builder"
  }
}
