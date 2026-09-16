# Use the official Node image (Alpine is a super lightweight Linux version)
FROM node:20-alpine

# Set the working directory
WORKDIR /app

# Copy only the package files first (This is a Docker caching trick!)
COPY package.json package-lock.json* ./

# Install the Node dependencies
RUN npm install

# Copy the rest of your application code
COPY . .

# Expose the port Next.js uses
EXPOSE 3000

# Run the development server
CMD ["npm", "run", "dev"]
