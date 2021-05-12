# KubeCepops

一个基于Kubernetes的复杂事件处理单元部署系统

## Raspberry Pi OS（树莓派）预安装步骤

### 系统准备

刷好树莓派系统镜像后首先在SD卡根目录放一个名叫ssh的空文件（用以开启树莓派ssh功能）  
进入系统后按对应node角色修改/etc/hostname中的名字（必须小写）  
按对应node角色修改/etc/hosts中的名字（必须小写）  
如：kubernetes-master-01、kubernetes-worker-01、kubernetes-worker-02、kubernetes-worker-03、kubernetes-worker-04等 最后重启  
换源：

```
sudo vi /etc/apt/sources.list
```

注释掉原来的后加上：
> deb http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ buster main non-free contrib rpi  
deb-src http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ buster main non-free contrib rpi

```
sudo vi /etc/apt/sources.list.d/raspi.list
```

注释掉原来的后加上：
> deb http://mirrors.tuna.tsinghua.edu.cn/raspberrypi/ buster main ui

### 安装准备

关闭swap：

```
sudo vi /etc/dphys-swapfile
```

将CONF_SWAPSIZE修改为0  
开放端口（这里为了方便直接全部打开了 严格来说应该按照官方文档要求仅打开需要的端口）：

```
sudo iptables -P INPUT ACCEPT

sudo iptables -P OUTPUT ACCEPT
```

下面这两步应该可以写成一句 但是貌似有权限问题 先输出再移动过去可解决：

```
sudo iptables-save > /home/pi/iptables.rules

sudo mv /home/pi/iptables.rules /etc/iptables.rules

sudo vi /etc/network/if-pre-up.d/iptables
```

输入：
> \# !/bin/bash  
iptables-restore < /etc/iptables.rules

```
sudo chmod +x /etc/network/if-pre-up.d/iptables

sudo vi /boot/cmdline.txt
```

头部添加（注意末尾与原先内容用空格隔开）：
> cgroup_enable=memory cgroup_memory=1

```
sudo reboot
```

### 安装容器运行时

```
sudo apt-get update

sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common

curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -

sudo apt-key fingerprint 0EBFCD88

echo "deb [arch=armhf] https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/debian \
     $(lsb_release -cs) stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list

sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io

sudo vi /usr/lib/systemd/system/docker.service
```

将ExecStart改为：
> ExecStart=/usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock --exec-opt native.cgroupdriver=systemd

设置docker代理（可选 如果需要科学上网的话）：

```
sudo mkdir -p /etc/systemd/system/docker.service.d

sudo vi /etc/systemd/system/docker.service.d/http-proxy.conf
```

输入以下内容：
> [Service]  
Environment="HTTP_PROXY=socks5://<此处替换为你本机的IP>:<此处替换为科学上网工具所提供socks5转发服务的端口>"  
Environment="HTTPS_PROXY=socks5://<此处替换为你本机的IP>:<此处替换为科学上网工具所提供socks5转发服务的端口>"  
Environment="NO_PROXY=localhost,127.0.0.1"

```
sudo systemctl daemon-reload

sudo systemctl restart docker

sudo docker run hello-world

sudo reboot
```

### 安装 kubeadm kubectl kubelet

buster版本暂时没有 这里用的stretch
更新见 https://mirrors.tuna.tsinghua.edu.cn/help/kubernetes/ https://mirrors.tuna.tsinghua.edu.cn/kubernetes/apt/dists/

```
sudo apt-get update && sudo apt-get install -y apt-transport-https curl

curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

# 如果需要科学上网 上一句可替换为：
# curl --socks5 <此处替换为你本机的IP>:<此处替换为科学上网工具所提供socks5转发服务的端口> -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

cat <<EOF | sudo tee /etc/apt/sources.list.d/kubernetes.list
deb https://mirrors.tuna.tsinghua.edu.cn/kubernetes/apt kubernetes-stretch main
EOF

sudo apt-get update

sudo apt-get install -y kubelet kubeadm kubectl

sudo apt-mark hold kubelet kubeadm kubectl
```

### 启动集群

```
sudo kubeadm init --pod-network-cidr=10.244.0.0/16 --ignore-preflight-errors=Mem --image-repository registry.aliyuncs.com/google_containers

mkdir -p $HOME/.kube

sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config

sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

其中$HOME/.kube/config文件可以复制出来到项目根目录下的kubecepops.kubetools目录下备用

### 安装pod网络

一般来说 由于 raw.githubusercontent.com 域名被墙 直接安装会失效 所以这里采取修改hosts的方法进行安装  
先访问 https://www.ipaddress.com/ 查询 raw.githubusercontent.com 的IP地址  
获得IP地址后：

```
sudo vi /etc/hosts
```

加入以下条目：
> <此处替换为获得的IP地址> raw.githubusercontent.com

```
sudo reboot
```

这里直接执行可能还是不通 可以先ping一下获得的IP地址或者 raw.githubusercontent.com 后再试试

```
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```

### 加入worker节点

```
kubeadm token create
```

得到值1

```
openssl x509 -pubkey -in /etc/kubernetes/pki/ca.crt | openssl rsa -pubin -outform der 2>/dev/null | \
   openssl dgst -sha256 -hex | sed 's/^.* //'
```

得到值2  
在要加入的节点上输入：

```
sudo kubeadm join <master节点IP>:6443 --token <值1> \
    --discovery-token-ca-cert-hash sha256:<值2>
```

### 安装metrics-server

```
kubectl apply -f components.yaml
```

components.yaml为项目根目录下的文件 此为v0.4.2版本 也可以到 https://github.com/kubernetes-sigs/metrics-server/releases 选择最新版本
但是要在文件的Deployment中的spec.template.spec.- args中加上<- --kubelet-insecure-tls>的参数

### （可选）安装Dashboard UI

```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0/aio/deploy/recommended.yaml
```

在本节点直接运行：

```
kubectl proxy
```

开放给其它节点登录：

```
kubectl proxy --accept-hosts='^*$' --address='0.0.0.0'
```

在别的节点上设置一下端口转发 之后就可以用浏览器打开了：

```
ssh -L localhost:8001:localhost:8001 -NT pi@<master节点IP>
```

> http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/

新建文件dash-admin-user.yaml：
> apiVersion: v1  
kind: ServiceAccount  
metadata:  
name: admin-user  
namespace: kubernetes-dashboard
>
>\---  
apiVersion: rbac.authorization.k8s.io/v1  
kind: ClusterRoleBinding  
metadata:  
name: admin-user  
roleRef:  
apiGroup: rbac.authorization.k8s.io  
kind: ClusterRole  
name: cluster-admin  
subjects:  
\- kind: ServiceAccount  
name: admin-user  
namespace: kubernetes-dashboard

```
kubectl apply -f dash-admin-user.yaml

kubectl -n kubernetes-dashboard get secret $(kubectl -n kubernetes-dashboard get sa/admin-user -o jsonpath="{.secrets[0].name}") -o go-template="{{.data.token | base64decode}}"
```

得到token  
复制token到网页登录

***

## Ubuntu（虚拟机）预安装步骤

### 系统准备

进入系统后按对应node角色修改/etc/hostname中的名字（必须小写）  
按对应node角色修改/etc/hosts中的名字（必须小写）  
如：kubernetes-master-01、kubernetes-worker-01、kubernetes-worker-02、kubernetes-worker-03、kubernetes-worker-04等 最后重启  
换源：

```
sudo vi /etc/apt/sources.list
```

注释掉原来的后加上：
> /# 默认注释了源码镜像以提高 apt update 速度，如有需要可自行取消注释  
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal main restricted universe multiverse  
/# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal main restricted universe multiverse  
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-updates main restricted universe multiverse  
/# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-updates main restricted universe multiverse  
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-backports main restricted universe multiverse  
/# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-backports main restricted universe multiverse  
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-security main restricted universe multiverse  
/# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-security main restricted universe multiverse
>
>/# 预发布软件源，不建议启用  
/# deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-proposed main restricted universe multiverse  
/# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-proposed main restricted universe multiverse

### 安装准备

关闭swap：

```
sudo vi /etc/fstab
```

将/swapfile none swap sw 0 0注释掉  
开放端口（这里为了方便直接全部打开了 严格来说应该按照官方文档要求仅打开需要的端口）：

```
sudo iptables -P INPUT ACCEPT

sudo iptables -P OUTPUT ACCEPT
```

下面这两步应该可以写成一句 但是貌似有权限问题 先输出再移动过去可解决：

```
sudo iptables-save > /home/kyx1999/iptables.rules

sudo mv /home/kyx1999/iptables.rules /etc/iptables.rules

sudo vi /etc/network/if-pre-up.d/iptables
```

输入：
> \# !/bin/bash  
iptables-restore < /etc/iptables.rules

```
sudo chmod +x /etc/network/if-pre-up.d/iptables

sudo reboot
```

### 安装容器运行时

```
sudo apt-get update

sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo apt-key fingerprint 0EBFCD88

sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io

sudo vi /usr/lib/systemd/system/docker.service
```

将ExecStart改为：
> ExecStart=/usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock --exec-opt native.cgroupdriver=systemd

设置docker代理（可选 如果需要科学上网的话）：

```
sudo mkdir -p /etc/systemd/system/docker.service.d

sudo vi /etc/systemd/system/docker.service.d/http-proxy.conf
```

输入以下内容：
> [Service]  
Environment="HTTP_PROXY=socks5://<此处替换为你本机的IP>:<此处替换为科学上网工具所提供socks5转发服务的端口>"  
Environment="HTTPS_PROXY=socks5://<此处替换为你本机的IP>:<此处替换为科学上网工具所提供socks5转发服务的端口>"  
Environment="NO_PROXY=localhost,127.0.0.1"

```
sudo systemctl daemon-reload

sudo systemctl restart docker

sudo docker run hello-world

sudo reboot
```

### 安装 kubeadm kubectl kubelet

focal版本暂时没有 这里用的xenial
更新见 https://mirrors.tuna.tsinghua.edu.cn/help/kubernetes/ https://mirrors.tuna.tsinghua.edu.cn/kubernetes/apt/dists/

```
sudo apt-get update && sudo apt-get install -y apt-transport-https curl

curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

# 如果需要科学上网 上一句可替换为：
# curl --socks5 <此处替换为你本机的IP>:<此处替换为科学上网工具所提供socks5转发服务的端口> -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

cat <<EOF | sudo tee /etc/apt/sources.list.d/kubernetes.list
deb https://mirrors.tuna.tsinghua.edu.cn/kubernetes/apt kubernetes-xenial main
EOF

sudo apt-get update

sudo apt-get install -y kubelet kubeadm kubectl

sudo apt-mark hold kubelet kubeadm kubectl
```

### 启动集群

```
sudo kubeadm init --pod-network-cidr=10.244.0.0/16 --image-repository registry.aliyuncs.com/google_containers

mkdir -p $HOME/.kube

sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config

sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

其中$HOME/.kube/config文件可以复制出来到项目根目录下的kubecepops.kubetools目录下备用

### 安装pod网络

一般来说 由于 raw.githubusercontent.com 域名被墙 直接安装会失效 所以这里采取修改hosts的方法进行安装  
先访问 https://www.ipaddress.com/ 查询 raw.githubusercontent.com 的IP地址  
获得IP地址后：

```
sudo vi /etc/hosts
```

加入以下条目：
> <此处替换为获得的IP地址> raw.githubusercontent.com

```
sudo reboot
```

这里直接执行可能还是不通 可以先ping一下获得的IP地址或者 raw.githubusercontent.com 后再试试

```
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```

### 加入worker节点

```
kubeadm token create
```

得到值1

```
openssl x509 -pubkey -in /etc/kubernetes/pki/ca.crt | openssl rsa -pubin -outform der 2>/dev/null | \
   openssl dgst -sha256 -hex | sed 's/^.* //'
```

得到值2  
在要加入的节点上输入：

```
sudo kubeadm join <master节点IP>:6443 --token <值1> \
    --discovery-token-ca-cert-hash sha256:<值2>
```

### 安装metrics-server

```
kubectl apply -f components.yaml
```

components.yaml为项目根目录下的文件 此为v0.4.2版本 也可以到 https://github.com/kubernetes-sigs/metrics-server/releases 选择最新版本
但是要在文件的Deployment中的spec.template.spec.- args中加上<- --kubelet-insecure-tls>的参数

### （可选）安装Dashboard UI

```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0/aio/deploy/recommended.yaml
```

在本节点直接运行：

```
kubectl proxy
```

开放给其它节点登录：

```
kubectl proxy --accept-hosts='^*$' --address='0.0.0.0'
```

安装openssh-server以提供ssh登录服务 ubuntu默认不安装：

```
sudo apt-get install openssh-server
```

看有没有openssh-server：

```
dpkg -l | grep ssh
```

看有没有sshd：

```
ps -e | grep ssh
```

在别的节点上设置一下端口转发 之后就可以用浏览器打开了：

```
ssh -L localhost:8001:localhost:8001 -NT kyx1999@<master节点IP>
```

> http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/

新建文件dash-admin-user.yaml：
> apiVersion: v1  
kind: ServiceAccount  
metadata:  
name: admin-user  
namespace: kubernetes-dashboard
>
>\---  
apiVersion: rbac.authorization.k8s.io/v1  
kind: ClusterRoleBinding  
metadata:  
name: admin-user  
roleRef:  
apiGroup: rbac.authorization.k8s.io  
kind: ClusterRole  
name: cluster-admin  
subjects:  
\- kind: ServiceAccount  
name: admin-user  
namespace: kubernetes-dashboard

```
kubectl apply -f dash-admin-user.yaml

kubectl -n kubernetes-dashboard get secret $(kubectl -n kubernetes-dashboard get sa/admin-user -o jsonpath="{.secrets[0].name}") -o go-template="{{.data.token | base64decode}}"
```

得到token  
复制token到网页登录

***

## 常用命令

### 查看kubelet日志

```
sudo systemctl status kubelet
sudo journalctl -xeu kubelet
```

### 重置节点（同时从集群中删除该节点）

```
sudo kubeadm reset
sudo iptables -F && iptables -t nat -F && iptables -t mangle -F && iptables -X
```

### 删除Dashboard UI

```
kubectl delete -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0/aio/deploy/recommended.yaml
```

### 登录Docker Hub

```
sudo docker login
```

### 打包镜像

在Dockerfile所在的目录下（即项目根目录）：

```
sudo docker build -t kubecepops:latest .
```

查看kubecepops:latest的IMAGE ID：

```
sudo docker images

sudo docker run -d <此处替换为得到的IMAGE ID>
```

得到值1

```
sudo docker commit <此处替换为值1> <此处替换为镜像仓库（不带tag）>

sudo docker push <此处替换为镜像仓库>
```

### 清理结束运行的容器

```
sudo docker container prune
```

### 删除镜像

```
sudo docker rmi <要删除的IMAGE ID>
```
