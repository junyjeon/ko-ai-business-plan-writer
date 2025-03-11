# 📁 **Cursor AI IDE 작업 규칙(cursor.rules.md)**

이 문서는 **Cursor AI IDE**를 활용한 코드 작성 과정에서 할루시네이션(Hallucination) 현상을 방지하고, 명확한 코드 품질을 보장하기 위한 규칙 및 방법론을 정의한다.

---

## 🚩 **1. 기본 원칙 (General Guidelines)**

- **단일 책임 원칙(Single Responsibility Principle)**을 엄격히 준수한다.
  - 한 파일은 한 가지 명확한 기능과 책임만 수행한다.
  - 클래스와 함수는 최소 단위로 작성한다.

- 기존 코드의 변경은 명시적인 요청이나 승인이 없는 한 금지한다.
  - 수정 시 반드시 사용자에게 승인 요청한다.

- 요청 맥락이 명확하지 않은 경우, AI는 반드시 사용자에게 추가적인 질문을 해야 한다.

---

## 📌 **폴더 구조 규칙 (Folder Structure Guidelines)**

AI가 작업할 때 아래의 구조를 반드시 따라야 한다.

```plaintext
ProjectRoot/
├── features/
│   ├── userAuth/
│   │   ├── LoginValidator.ts
│   │   ├── SessionManager.ts
│   │   └── AuthAPIHandler.ts
│   └── payment/
│       └── PaymentProcessor.ts
│
├── core/
│   ├── interfaces/
│   ├── models/
│   └── services/
│
└── shared/
    ├── components/
    ├── constants/
    └── utils/
```

- 각 기능 단위는 독립된 폴더로 분리한다.
- AI는 주어진 폴더 구조를 벗어나 작업하지 않는다.

---

## 🚩 **AI의 작업 수행 규칙**

- AI는 요청된 작업 범위를 초과하여 임의로 확장하지 않는다.
- 가능한 최소한의 코드 변경을 수행하고, 코드를 새로 작성할 경우 최소한의 분량으로 작성한다.
- 사용자의 요청을 정확히 이해하지 못했을 때는, 추측하거나 추론하지 않고 사용자에게 명확한 추가 정보를 요청한다.

---

## 📌 **권장 디자인 패턴과 예시**

아래의 디자인 패턴은 AI가 코드를 구조화하는 데 적극 활용해야 하며, 그 외 패턴 사용 시 사용자와 협의한다.

| 디자인 패턴 | 적용 목적 |
|---|---|
| **팩토리 메서드 (Factory Method)** | 객체 생성 로직 분리 |
| **전략 패턴 (Strategy)** | 로직의 명확한 분리 및 독립적 관리 |
| **컴포지션 (Composition)** | 상속 대신 결합도 낮춘 모듈화 |
| **파사드 (Facade)** | 복잡한 로직을 단순 인터페이스로 관리 |

### ✅ **전략 패턴(Strategy Pattern) 예시 (C++)**

```cpp
// ILoggerStrategy.h
class ILoggerStrategy {
public:
  virtual void log(const std::string& message) = 0;
};
```

```cpp
// ConsoleLogger.h
#include "ILoggerStrategy.h"
#include <iostream>

class ConsoleLogger : public ILoggerStrategy {
public:
  void log(const std::string& message) override {
    std::cout << message << std::endl;
  }
};
```

```cpp
// FileLogger.h
#include <fstream>
#include "ILoggerStrategy.h"

class FileLogger : public ILoggerStrategy {
public:
  void log(const std::string& message) override {
    std::ofstream file("log.txt", std::ios_base::app);
    file << message << std::endl;
    file.close();
  }
};
```

```cpp
// LoggerContext.h
class LoggerContext {
public:
  LoggerContext(ILoggerStrategy* logger) : logger_(logger) {}

  void log(const std::string& message) {
    if (logger) logger->log(message);
  }

  void setLogger(ILoggerStrategy* logger) {
    loggerStrategy = logger;
  }

private:
  ILoggerStrategy* loggerStrategy = nullptr;
};
```

---

## 🔄 **작업 흐름(Workflow)**

AI가 생성한 모든 작업은 다음 프로세스를 준수해야 한다:

| 단계 | 설명 | 주체 |
|---|---|---|
| 작업 요청 | 작업 범위와 목적을 명확히 제공 | 사용자 |
| AI 코드 생성 | 명확한 범위 내에서 코드 작성 (임시 파일/폴더 활용) | Cursor AI |
| 리뷰 단계 | AI 결과물을 사용자가 검토 후 첨삭 | 사용자 |
| 통합 단계 | 리뷰 완료 후, 최종적으로 프로젝트에 병합 | 사용자 |

---

## 📑 **변경사항 관리 및 문서화 (Change Management)**

모든 작업은 명확히 기록되고 문서화되어야 한다.  
추천 기록 양식(예시: Notion, GitHub Wiki 활용):

| 날짜 | 작업 내용 | AI 결과 | 사용자의 리뷰사항 | 최종상태 |
|---|---|---|---|---|
| 2025-03-11 | 로그인 클래스 작성 | AI: 초안 작성 | 세션 관리 로직 보완 및 첨삭 | ✅ 최종 병합 완료 |

---

## 📌 🔑 **최종 기대 효과**

본 규칙을 엄격히 적용함으로써:

- AI의 할루시네이션 현상이 최소화됨.
- 코드 작성 과정에서 사용자와 AI 간의 오해가 현저히 감소함.
- 코드 품질이 높아지고 유지보수가 간편해짐.
- 생산성과 코드의 신뢰성이 높아짐.
