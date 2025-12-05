# Base 이미지: Node.js (Vite 프로젝트에 적합)
FROM node:18-alpine

# 컨테이너 내 작업 디렉토리 설정
WORKDIR /app

# package.json과 package-lock.json만 복사 (의존성 설치용)
COPY package*.json ./

# 의존성 설치
RUN npm install

# ⚠️ COPY . . 삭제! 
# 볼륨 마운트로 호스트 코드를 사용할 것이므로 복사 불필요

# Vite 개발 서버가 사용할 포트 노출
EXPOSE 3000

# 개발 서버 실행
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]