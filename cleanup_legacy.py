#!/usr/bin/env python
"""
레거시 파일 및 디렉토리 정리 스크립트
"""
import os
import sys
import shutil
import glob

# 삭제할 레거시 디렉토리 목록
LEGACY_DIRECTORIES = [
    "prompts",   # data/prompts로 이동됨
    "proposal",  # data/proposals로 이동됨
    "templates"  # data/templates로 이동됨
]

def check_and_remove_directory(dir_path):
    """
    디렉토리가 존재하면 삭제합니다.
    디렉토리 내 모든 파일도 함께 삭제됩니다.
    """
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        num_files = sum(len(files) for _, _, files in os.walk(dir_path))
        
        # 사용자 확인 요청
        confirm = input(f"'{dir_path}' 디렉토리와 내부 {num_files}개 파일을 삭제하시겠습니까? (y/n): ").strip().lower()
        
        if confirm == 'y':
            try:
                shutil.rmtree(dir_path)
                print(f"'{dir_path}' 디렉토리가 삭제되었습니다.")
                return True
            except Exception as e:
                print(f"오류: '{dir_path}' 디렉토리 삭제 중 문제 발생: {str(e)}")
                return False
        else:
            print(f"'{dir_path}' 디렉토리 삭제를 취소했습니다.")
            return False
    else:
        print(f"'{dir_path}' 디렉토리가 존재하지 않습니다.")
        return False

def cleanup_legacy_files():
    """
    이전 위치의 파일 및 디렉토리를 정리합니다.
    """
    print("\n===== 레거시 파일 및 디렉토리 정리 =====")
    print("새 구조로 마이그레이션된 후 불필요한 이전 디렉토리를 삭제합니다.\n")
    
    # 먼저 새 구조가 있는지 확인
    data_dir = "data"
    if not os.path.exists(data_dir) or not os.path.isdir(data_dir):
        print(f"오류: 새 구조의 '{data_dir}' 디렉토리를 찾을 수 없습니다.")
        print("삭제를 진행하기 전에 'python migrate.py'를 실행하여 파일을 마이그레이션하세요.")
        return False
    
    # 데이터 파일이 새 위치에 복사되었는지 확인
    required_subdirs = ["prompts", "proposals", "templates"]
    missing_dirs = [subdir for subdir in required_subdirs 
                   if not os.path.exists(os.path.join(data_dir, subdir))]
    
    if missing_dirs:
        print(f"오류: 새 구조에 필요한 하위 디렉토리가 없습니다: {', '.join(missing_dirs)}")
        print("삭제를 진행하기 전에 'python migrate.py'를 실행하여 파일을 마이그레이션하세요.")
        return False
    
    # 레거시 디렉토리 삭제
    removed_count = 0
    for legacy_dir in LEGACY_DIRECTORIES:
        if check_and_remove_directory(legacy_dir):
            removed_count += 1
    
    # 삭제 결과 요약
    print(f"\n총 {removed_count}/{len(LEGACY_DIRECTORIES)} 디렉토리가 삭제되었습니다.")
    
    return True

def main():
    """스크립트 메인 함수"""
    try:
        result = cleanup_legacy_files()
        return 0 if result else 1
    except KeyboardInterrupt:
        print("\n작업이 사용자에 의해 중단되었습니다.")
        return 1
    except Exception as e:
        print(f"\n오류 발생: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 