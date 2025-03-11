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

def copy_file(src, dst):
    """
    파일을 소스에서 대상 경로로 복사합니다
    대상 디렉토리가 없으면 자동으로 생성합니다
    """
    dst_dir = os.path.dirname(dst)
    ensure_dir_exists(dst_dir)
    
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"파일 복사됨: {src} -> {dst}")
        return True
    else:
        print(f"오류: 소스 파일이 존재하지 않음: {src}")
        return False

def migrate_templates():
    """
    템플릿 파일을 레거시 위치에서 새 위치로 복사합니다
    """
    legacy_dir = "templates"
    new_dir = os.path.join("data", "templates")
    ensure_dir_exists(new_dir)
    
    if os.path.exists(legacy_dir) and os.path.isdir(legacy_dir):
        # 템플릿 디렉토리 내 모든 파일 복사
        files_copied = 0
        for file_name in os.listdir(legacy_dir):
            src_path = os.path.join(legacy_dir, file_name)
            dst_path = os.path.join(new_dir, file_name)
            
            if os.path.isfile(src_path):
                if copy_file(src_path, dst_path):
                    files_copied += 1
        
        print(f"{files_copied}개의 템플릿 파일이 새 위치로 복사되었습니다.")
        return files_copied
    else:
        print(f"경고: 레거시 템플릿 디렉토리를 찾을 수 없습니다: {legacy_dir}")
        return 0

if __name__ == "__main__":
    # 이 파일을 직접 실행하면 템플릿 이동 작업 수행
    migrate_templates() 