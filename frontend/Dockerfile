# Step 1: Upgrade to Node 20 Alpine to support node:util styleText
FROM node:20-alpine

# Step 2: Set application directory
WORKDIR /app

# Step 3: Copy package files
COPY package*.json ./

# Step 4: Install Node modules
RUN npm install

# Step 5: Copy application source code
COPY . .

# Step 6: Expose Vite default container port
EXPOSE 3000

# Step 7: Start Vite development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]