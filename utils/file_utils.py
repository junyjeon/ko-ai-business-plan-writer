"""
파일 처리 관련 유틸리티 함수
"""
import os
import shutil

def ensure_dir_exists(path):
    """
    디렉토리가 존재하지 않으면 생성합니다
    """
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        print(f"디렉토리 생성됨: {path}")
    return path

def move_file(src, dst):
    """
    파일을 소스에서 대상 경로로 이동합니다
    대상 디렉토리가 없으면 자동으로 생성합니다
    """
    dst_dir = os.path.dirname(dst)
    ensure_dir_exists(dst_dir)
    
    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"파일 이동됨: {src} -> {dst}")
    else:
        print(f"오류: 소스 파일이 존재하지 않음: {src}") 