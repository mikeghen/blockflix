provider "aws" {}

# Create a VPC to launch our instances into
resource "aws_vpc" "default" {
  cidr_block = "10.0.0.0/16"

  tags {
    Name = "data-platform"
    Project = "data-platform"
  }
}

# Create an internet gateway to give our subnet access to the outside world
resource "aws_internet_gateway" "default" {
  vpc_id = "${aws_vpc.default.id}"

  tags {
    Name = "data-platform"
    Project = "data-platform"
  }
}

# Grant the VPC internet access on its main route table
resource "aws_route" "internet_access" {
  route_table_id         = "${aws_vpc.default.main_route_table_id}"
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = "${aws_internet_gateway.default.id}"
}

# Create a subnet to launch our instances into
resource "aws_subnet" "default" {
  vpc_id                  = "${aws_vpc.default.id}"
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone = "us-west-2a"

  tags {
    Name = "data-platform-default"
    Project = "data-platform"
  }
}

resource "aws_subnet" "secondary" {
  vpc_id                  = "${aws_vpc.default.id}"
  cidr_block              = "10.0.2.0/24"
  map_public_ip_on_launch = true
  availability_zone = "us-west-2b"

  tags {
    Name = "data-platform-secondary"
    Project = "data-platform"
  }
}

# Create a DB subnet for RDS
resource "aws_db_subnet_group" "default" {
  name       = "database-subnet"
  subnet_ids = ["${aws_subnet.default.id}","${aws_subnet.secondary.id}"]

  tags {
    Name = "Database Subnet Group"
  }
}

# Our application security group to access
# application servers over SSH and HTTP
resource "aws_security_group" "application_sg" {
  name        = "application_sq"
  description = "Application Security Group"
  vpc_id      = "${aws_vpc.default.id}"

  # SSH access from anywhere
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["108.2.133.64/32"]
  }

  # HTTP access from the VPC
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["108.2.133.64/32"]
  }

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["108.2.133.64/32"]
  }

  ingress {
    from_port   = 2992
    to_port     = 2992
    protocol    = "tcp"
    cidr_blocks = ["108.2.133.64/32"]
  }

  # outbound internet access
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["108.2.133.64/32"]
  }
}

# Our database security group to access
# database servers internally
resource "aws_security_group" "database_sg" {
  name        = "database_sg"
  description = "Database Security Group"
  vpc_id      = "${aws_vpc.default.id}"

  # MySQL access from application_sg
  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    security_groups = ["${aws_security_group.application_sg.id}"]
  }

  # outbound internet access
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_key_pair" "auth" {
  key_name   = "ghen-workstation"
  public_key = "${file("/Users/mikeghen/.ssh/id_rsa.pub")}"
}

resource "aws_instance" "redash" {
  # The connection block tells our provisioner how to
  # communicate with the resource (instance)
  connection {
    # The default username for our AMI
    user = "ubuntu"
    # The connection will use the local SSH agent for authentication.
  }

  instance_type = "t2.micro"

  ami = "ami-2325c85b" # https://redash.io/help/open-source/setup#aws

  # The name of our SSH keypair we created above.
  key_name = "${aws_key_pair.auth.id}"

  # Our Security group to allow HTTP and SSH access
  vpc_security_group_ids = ["${aws_security_group.application_sg.id}"]

  # We're going to launch into the same subnet as our ELB. In a production
  # environment it's more common to have a separate private subnet for
  # backend instances.
  subnet_id = "${aws_subnet.default.id}"

  tags {
    Name = "redash"
    Project = "data-platform"
  }
}

resource "aws_instance" "blockflix" {
  # The connection block tells our provisioner how to
  # communicate with the resource (instance)
  connection {
    # The default username for our AMI
    user = "ubuntu"

    # The connection will use the local SSH agent for authentication.
  }

  instance_type = "t2.large"

  # Lookup the correct AMI based on the region
  # we specified
  ami = "ami-51537029"

  # The name of our SSH keypair we created above.
  key_name = "${aws_key_pair.auth.id}"

  # Our Security group to allow HTTP and SSH access
  vpc_security_group_ids = ["${aws_security_group.application_sg.id}"]

  # We're going to launch into the same subnet as our ELB. In a production
  # environment it's more common to have a separate private subnet for
  # backend instances.
  subnet_id = "${aws_subnet.default.id}"

  tags {
    Name = "blockflix"
    Project = "data-platform"
  }

  # We run a remote provisioner on the instance after creating it.
  # In this case, we just install nginx and start it. By default,
  # this should be on port 80
  # provisioner "remote-exec" {
  #   inline = [
  #     "sudo apt-get -y update",
  #     "sudo apt-get -y install python3-pip nodejs npm libmysqlclient-dev",
  #     "cd /opt",
  #     "sudo git clone https://github.com/mikeghen/blockflix",
  #     "cd blockflix",
  #     ""
  #   ]
  # }
}

resource "aws_db_instance" "blockflix_db" {
  depends_on             = ["aws_security_group.database_sg"]
  identifier             = "blockflix-dev-db"
  allocated_storage      = 25
  engine                 = "mysql"
  engine_version         = "5.7"
  instance_class         = "db.t2.micro"
  name                   = "blockflix_development"
  username               = "blockflix"
  password               = "blockflix"
  vpc_security_group_ids = ["${aws_security_group.database_sg.id}"]
  db_subnet_group_name   = "${aws_db_subnet_group.default.id}"
}

output "db_instance_address" {
  value = "${aws_db_instance.blockflix_db.address}"
}

output "redash_instance_address" {
  value = "${aws_instance.redash.public_ip}"
}

output "blockflix_instance_address" {
  value = "${aws_instance.blockflix.public_ip}"
}
