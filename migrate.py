#!/usr/bin/env python
"""
기존 파일 구조에서 새 구조로 파일을 마이그레이션하는 스크립트
"""
import os
import sys
import glob
from utils.file_utils import ensure_dir_exists, copy_file

def migrate_prompts():
    """프롬프트 파일을 prompts/ 에서 data/prompts/로 복사"""
    legacy_dir = "prompts"
    new_dir = os.path.join("data", "prompts")
    ensure_dir_exists(new_dir)
    
    if os.path.exists(legacy_dir) and os.path.isdir(legacy_dir):
        txt_files = glob.glob(os.path.join(legacy_dir, "*.txt"))
        files_copied = 0
        
        for src_path in txt_files:
            file_name = os.path.basename(src_path)
            dst_path = os.path.join(new_dir, file_name)
            
            if copy_file(src_path, dst_path):
                files_copied += 1
        
        print(f"{files_copied}개의 프롬프트 파일이 새 위치로 복사되었습니다.")
        return files_copied
    else:
        print(f"경고: 레거시 프롬프트 디렉토리를 찾을 수 없습니다: {legacy_dir}")
        return 0

def migrate_proposals():
    """기획서 파일을 proposal/ 에서 data/proposals/로 복사"""
    legacy_dir = "proposal"
    new_dir = os.path.join("data", "proposals")
    ensure_dir_exists(new_dir)
    
    if os.path.exists(legacy_dir) and os.path.isdir(legacy_dir):
        txt_files = glob.glob(os.path.join(legacy_dir, "*.txt"))
        files_copied = 0
        
        for src_path in txt_files:
            file_name = os.path.basename(src_path)
            dst_path = os.path.join(new_dir, file_name)
            
            if copy_file(src_path, dst_path):
                files_copied += 1
        
        print(f"{files_copied}개의 기획서 파일이 새 위치로 복사되었습니다.")
        return files_copied
    else:
        print(f"경고: 레거시 기획서 디렉토리를 찾을 수 없습니다: {legacy_dir}")
        return 0

def migrate_templates():
    """템플릿 파일을 templates/ 에서 data/templates/로 복사"""
    from utils.file_utils import migrate_templates
    return migrate_templates()

def main():
    """모든 마이그레이션 작업 수행"""
    print("\n===== 파일 마이그레이션 도구 =====")
    print("기존 파일 구조에서 새 구조로 파일을 복사합니다.\n")
    
    # 마이그레이션 작업 수행
    prompt_count = migrate_prompts()
    proposal_count = migrate_proposals()
    template_count = migrate_templates()
    
    # 결과 요약
    print("\n===== 마이그레이션 결과 =====")
    print(f"- 프롬프트 파일: {prompt_count}개")
    print(f"- 기획서 파일: {proposal_count}개")
    print(f"- 템플릿 파일: {template_count}개")
    
    total = prompt_count + proposal_count + template_count
    print(f"\n총 {total}개 파일이 새 구조로 복사되었습니다.")
    
    if total > 0:
        print("\n참고: 기존 파일은 삭제되지 않았습니다. 필요하지 않다면 수동으로 삭제하세요.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 