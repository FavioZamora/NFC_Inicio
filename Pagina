<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Login NFC + Blockchain</title>
<style>
body {
  background: linear-gradient(135deg, #1a237e, #283593);
  color: white;
  font-family: Arial, sans-serif;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
}
form {
  background: rgba(255, 255, 255, 0.1);
  padding: 2rem;
  border-radius: 10px;
  width: 300px;
  text-align: center;
}
input {
  width: 90%;
  padding: 10px;
  margin: 10px 0;
  border: none;
  border-radius: 5px;
}
button {
  padding: 10px;
  width: 100%;
  background: #00c853;
  border: none;
  color: white;
  border-radius: 5px;
  cursor: pointer;
}
button:hover {
  background: #00e676;
}
#result {
  margin-top: 15px;
  white-space: pre-line;
}
</style>
</head>
<body>
  <form id="loginForm">
    <h2>Autenticación NFC</h2>
    <input type="text" id="nfc_id" placeholder="UID NFC" required>
    <input type="password" id="pin" placeholder="PIN" required>
    <button type="submit">Iniciar Sesión</button>
    <div id="result"></div>
  </form>

<script>
document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  
  const nfc_id = document.getElementById("nfc_id").value.trim();
  const pin = document.getElementById("pin").value.trim();
  const device_id = "web_client_01";
  
  const res = document.getElementById("result");
  res.textContent = "⏳ Autenticando...";
  
  try {
    const response = await fetch("http://localhost:8000/authenticate", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({nfc_id, pin, device_id})
    });
    
    const data = await response.json();
    
    if (data.success) {
      res.textContent = `✅ ${data.message}\n👤 ${data.user.full_name}\n🏢 ${data.user.department}\n🔗 Tx: ${data.blockchain_tx}`;
    } else {
      res.textContent = `❌ ${data.message}`;
    }
  } catch (err) {
    res.textContent = "⚠️ Error al conectar con el servidor.";
  }
});
</script>
</body>
</html>
