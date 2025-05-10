FROM node:16-alpine

WORKDIR /app

# Copy package.json và package-lock.json
COPY my-app/package*.json ./

# Cài đặt dependencies
RUN npm install
# Cài đặt thêm axios và babel plugin
RUN npm install --save axios @babel/plugin-proposal-private-property-in-object

# Copy toàn bộ code
COPY my-app/ .

# Build ứng dụng
RUN npm run build

# Cài đặt serve để chạy production build
RUN npm install -g serve

# Expose cổng
EXPOSE 3000

# Chạy ứng dụng
CMD ["serve", "-s", "build", "-l", "3000"] 