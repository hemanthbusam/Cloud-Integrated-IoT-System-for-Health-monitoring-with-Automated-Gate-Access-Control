from inference_sdk import InferenceHTTPClient
import gradio as gr

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="Jtwl6gEJyH1vr1Qom11a"
)

def inference(image):
  try:
    result = CLIENT.infer(image, model_id="mask-detection-qwd3s/2")
    # Process the result (e.g., extract predictions)
    # Example: Assuming result contains a 'predictions' field
    return result
    # predictions = result.get('predictions', [])
    # # Create a formatted string to display predictions
    # prediction_string = ""
    # for prediction in predictions:
    #   prediction_string += f"{prediction.get('class')} - Confidence: {prediction.get('confidence')}\n"
    # return prediction_string
  except Exception as e:
      return f"Error during inference: {e}"

iface = gr.Interface(
    fn=inference,
    inputs=gr.Image(type="filepath"),
    outputs="text",
    title="Mask Detection",
    description="Upload an image to detect masks."
)

iface.launch(debug=True, inline=False, share=True )
