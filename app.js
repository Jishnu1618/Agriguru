async function submitImage() {
  const input = document.getElementById("imageInput");
  const file = input.files[0];

  if (!file) {
    alert("Please select an image.");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("http://127.0.0.1:8000/predict_disease", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    const resultDiv = document.getElementById("result");
    resultDiv.innerHTML = `
      <strong>Disease:</strong> ${data.predicted_disease}<br/>
      <strong>Confidence:</strong> ${data.confidence}<br/>
      <strong>Cure:</strong> ${data.suggested_cure}
    `;
  } catch (error) {
    alert("Error detecting disease. Make sure backend is running.");
    console.error(error);
  }
}
