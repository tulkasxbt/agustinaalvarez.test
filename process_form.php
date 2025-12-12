<?php
session_start();

// Configurar cabecera JSON
header('Content-Type: application/json');

// Validar que el formulario se haya enviado mediante POST
if ($_SERVER["REQUEST_METHOD"] !== "POST") {
    echo json_encode(["error" => "Método no permitido"]);
    exit;
}

// FUNCIONES DE VALIDACIÓN
function validarNombre($nombre) {
    return preg_match("/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s'-]{3,50}$/", $nombre);
}

function validarEmail($email) {
    return filter_var($email, FILTER_VALIDATE_EMAIL);
}

function validarTelefono($telefono) {
    return preg_match("/^\+54\d{10,13}$/", $telefono);
}

// OBTENER DATOS DEL FORMULARIO Y LIMPIARLOS
$nombre = trim($_POST['name'] ?? '');
$email = trim($_POST['email'] ?? '');
$telefono = trim($_POST['phone'] ?? '');
$fakeField = $_POST['fakefield'] ?? ''; // Campo honeypot oculto

// DETECTAR SPAM (honeypot)
if (!empty($fakeField)) {
    echo json_encode(["error" => "SPAM detectado"]);
    exit;
}

// FILTRO ANTI-SPAM: Verificar si la IP ha enviado demasiadas solicitudes en poco tiempo
$ip = $_SERVER['REMOTE_ADDR'];
if (!isset($_SESSION['last_submit_time'][$ip])) {
    $_SESSION['last_submit_time'][$ip] = time();
} else {
    $timeSinceLastSubmit = time() - $_SESSION['last_submit_time'][$ip];
    if ($timeSinceLastSubmit < 30) { // Solo permite 1 envío cada 30 segundos por IP
        echo json_encode(["error" => "Demasiadas solicitudes. Intenta en 30 segundos."]);
        exit;
    }
    $_SESSION['last_submit_time'][$ip] = time();
}

// VALIDACIONES
if (!validarNombre($nombre)) {
    echo json_encode(["error" => "Nombre inválido. Debe contener al menos 3 caracteres y menos de 50."]);
    exit;
}

if (!validarEmail($email)) {
    echo json_encode(["error" => "Correo electrónico no válido."]);
    exit;
}

if (!validarTelefono($telefono)) {
    echo json_encode(["error" => "Número de teléfono no válido. Debe ser argentino (+54) seguido de 10-13 dígitos."]);
    exit;
}

// GUARDAR DATOS EN CSV
$archivo_csv = 'datos_clientes.csv';
$existe_archivo = file_exists($archivo_csv);
$archivo = fopen($archivo_csv, 'a');

if (!$existe_archivo) {
    fputcsv($archivo, ['Nombre', 'Email', 'Teléfono']);
}

fputcsv($archivo, [$nombre, $email, $telefono]);
fclose($archivo);

// RESPUESTA JSON
echo json_encode([
    "success" => true,
    "nombre" => $nombre,
    "email" => $email,
    "telefono" => $telefono
]);
?>
