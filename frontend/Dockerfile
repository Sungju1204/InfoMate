# Base 이미지: Node.js (Vite 프로젝트에 적합)
FROM node:18-alpine

# 컨테이너 내 작업 디렉토리 설정
WORKDIR /app

# package.json과 package-lock.json 복사 (캐싱 활용)
COPY package*.json ./

# 의존성 설치
RUN npm install

# 나머지 파일 복사
COPY . .

# Vite 개발 서버가 사용할 포트 노출
EXPOSE 3000

# 개발 서버 실행
# 'npm run dev'는 package.json에 정의된 개발 명령어입니다.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]