import streamlit as st
import requests

# Set the title of the app
st.title("Blog Generator")

# Create a text input widget for the user to enter a blog topic
blog_topic = st.text_input("Enter the blog topic", "")
#blog_topic = input("Enter the blog topic:")
# Function to invoke the blog generation API with the user's topic
def generate_blog(topic):
    url = "https://e9z22xobha.execute-api.us-east-1.amazonaws.com/dev/blog-generation"  # Replace with your actual API endpoint
    payload = {"blog_topic": topic}
    response = requests.post(url, json=payload)
    #print(response.text)
    
    try:
        response_json = response.json()  # Attempt to parse the response as JSON
        return response_json
    except ValueError:
        st.error("Failed to parse response as JSON.")
        st.write(response.text)  # Display the raw response text for debugging
        return None

# Check if the user has entered a blog topic
if blog_topic:
    # Create a button to generate the blog
    if st.button("Generate Blog"):
        # Invoke the API with the user's topic
        blog_response = generate_blog(blog_topic)

        # Display the generated blog content
        if blog_response:
            st.subheader("Generated Blog")
            st.write(blog_response["blog_content"])
            st.info(blog_response["status"])
        else:
            st.error("Failed to generate blog. Please try again.")

# Add some instructions for the user
st.write("Enter a topic to generate a blog on that topic and press 'Generate Blog'.")