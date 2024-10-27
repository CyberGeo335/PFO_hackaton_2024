# Step 1: Use an official Node.js image as the base image
FROM node:16-alpine

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy the package.json and package-lock.json files to install dependencies
COPY package*.json ./

# Step 4: Install dependencies
RUN npm install

# Step 5: Copy the rest of the application code
COPY . .

# Step 6: Build the React app
RUN npm run build

# Step 7: Serve the application using a lightweight web server
# Install the 'serve' package globally to serve the production build
RUN npm install -g serve

# Step 8: Expose port 3000 to access the application
EXPOSE 3000

# Step 9: Start the server to serve the build files
CMD ["serve", "-s", "build", "-l", "3000"]
