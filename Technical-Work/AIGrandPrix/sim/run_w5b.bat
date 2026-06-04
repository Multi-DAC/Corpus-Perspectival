@echo off
cd /d "C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\sim"
set PYTHONIOENCODING=utf-8
python -u train_infinite_v3.py --total-steps 40000000 --n-envs 8 --perception-obs --ground-start-prob 0.5 --tag vq1_vision_w5b > vq1_vision_w5b.log 2>&1
