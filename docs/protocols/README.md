# 通信协议

通信分为两部分：控制和图传。

控制中，客户端和服务端均将信息以JSON格式序列化后传输，保证传输可靠性。具体序列化格式见[仓库](https://github.com/MosHumanoid/SDK/blob/main/docs/protocols/schemas)。

图传通过RTSP协议，服务端将图像数据以JPEG格式编码后传输，保证传输速度。
