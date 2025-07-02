from ultralytics import YOLO

model = YOLO('yolov8s.pt')
model.train(data='dataset/data.yaml', epochs=50, imgsz=640)