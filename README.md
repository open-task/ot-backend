# ot-backend

## 部署
```zsh
pip install -r requirements.txt
gunicorn task:app -p task.pid -b 0.0.0.0:5236 -D
```
