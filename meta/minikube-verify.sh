#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Update package lists
echo "Updating package lists..."
sudo apt update

# Check if Docker is running
if ! pgrep -x "docker" >/dev/null; then
    echo "Docker is not running. Please start Docker."
    exit 1
else
    sudo sed -i '/accept-nvidia-visible-devices-as-volume-mounts/c\accept-nvidia-visible-devices-as-volume-mounts = true' /etc/nvidia-container-runtime/config.toml
    echo "Docker is running."
fi

# Check if kind is installed
if ! command_exists minikube; then
    echo "minikube is not installed. Please install minikube."
    exit 1
else
    echo "minikube is installed."
fi

# Check if kubectl is installed
if ! command_exists kubectl; then
    echo "kubectl is not installed. Please install kubectl."
    exit 1
else
    echo "kubectl is installed."
fi

echo "Follow up and create your minikube cluster ⚡"
