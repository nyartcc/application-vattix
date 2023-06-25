/*terraform {
  cloud {
    organization = "NYARTCC"

    workspaces {
      name = "VATTIX_Local_Dev"
    }
  }
}*/

provider "aws" {
  region = var.aws_region
}