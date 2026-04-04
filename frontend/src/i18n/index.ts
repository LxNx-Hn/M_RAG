import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

const ko = {
  common: {
    appName: 'M-RAG',
    appDesc: '모듈러 RAG 논문 리뷰 에이전트',
    loading: '로딩 중...',
    error: '오류가 발생했습니다',
    cancel: '취소',
    confirm: '확인',
    delete: '삭제',
    save: '저장',
    close: '닫기',
  },
  topbar: {
    darkMode: '다크 모드',
    lightMode: '라이트 모드',
    language: '언어',
    login: '로그인',
    logout: '로그아웃',
    settings: '설정',
  },
  source: {
    title: '소스',
    upload: '파일 업로드',
    uploadHint: 'PDF, DOCX 파일을 드래그하거나 클릭하세요',
    uploading: '업로드 중...',
    papers: '업로드된 논문',
    noPapers: '아직 업로드된 논문이 없습니다',
    chunks: '청크',
    pages: '페이지',
    delete: '삭제',
    deleteConfirm: '이 논문을 삭제하시겠습니까?',
  },
  viewer: {
    title: '문서 뷰어',
    noPaper: '좌측에서 논문을 선택하세요',
    page: '페이지',
    of: '/',
    zoomIn: '확대',
    zoomOut: '축소',
    fitWidth: '너비 맞춤',
  },
  chat: {
    title: '채팅',
    placeholder: '논문에 대해 질문하세요...',
    send: '전송',
    newChat: '새 대화',
    noMessages: '논문에 대해 궁금한 것을 물어보세요!',
    route: '파이프라인',
    sources: '출처',
    streaming: '답변 생성 중...',
    searchOnly: '검색 결과만 표시됩니다 (GPU 모델 미로드)',
    suggestions: {
      q1: '이 논문의 핵심 기여가 뭐야?',
      q2: '실험 결과가 어떻게 나왔어?',
      q3: '사용한 방법론을 설명해줘',
      q4: '이 논문 전체 요약해줘',
      q5: '인용 논문들 분석해줘',
    },
  },
  history: {
    title: '대화 기록',
    empty: '대화 기록이 없습니다',
  },
}

const en: typeof ko = {
  common: {
    appName: 'M-RAG',
    appDesc: 'Modular RAG Paper Review Agent',
    loading: 'Loading...',
    error: 'An error occurred',
    cancel: 'Cancel',
    confirm: 'Confirm',
    delete: 'Delete',
    save: 'Save',
    close: 'Close',
  },
  topbar: {
    darkMode: 'Dark Mode',
    lightMode: 'Light Mode',
    language: 'Language',
    login: 'Login',
    logout: 'Logout',
    settings: 'Settings',
  },
  source: {
    title: 'Sources',
    upload: 'Upload File',
    uploadHint: 'Drag & drop PDF, DOCX files here or click',
    uploading: 'Uploading...',
    papers: 'Uploaded Papers',
    noPapers: 'No papers uploaded yet',
    chunks: 'chunks',
    pages: 'pages',
    delete: 'Delete',
    deleteConfirm: 'Delete this paper?',
  },
  viewer: {
    title: 'Document Viewer',
    noPaper: 'Select a paper from the left panel',
    page: 'Page',
    of: '/',
    zoomIn: 'Zoom In',
    zoomOut: 'Zoom Out',
    fitWidth: 'Fit Width',
  },
  chat: {
    title: 'Chat',
    placeholder: 'Ask about the paper...',
    send: 'Send',
    newChat: 'New Chat',
    noMessages: 'Ask anything about your papers!',
    route: 'Pipeline',
    sources: 'Sources',
    streaming: 'Generating answer...',
    searchOnly: 'Search results only (GPU model not loaded)',
    suggestions: {
      q1: 'What is the key contribution of this paper?',
      q2: 'How did the experiments turn out?',
      q3: 'Explain the methodology',
      q4: 'Summarize the entire paper',
      q5: 'Analyze the cited papers',
    },
  },
  history: {
    title: 'Chat History',
    empty: 'No conversations yet',
  },
}

i18n.use(initReactI18next).init({
  resources: {
    ko: { translation: ko },
    en: { translation: en },
  },
  lng: localStorage.getItem('language') || 'ko',
  fallbackLng: 'ko',
  interpolation: { escapeValue: false },
})

export default i18n
