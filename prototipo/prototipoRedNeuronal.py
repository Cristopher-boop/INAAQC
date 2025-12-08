import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pandas as pd

# Generación de datos sintéticos
np.random.seed(42)

def generar_datos(n, categoria):
    """Genera datos simulados para cada categoría médica."""
    if categoria == 0:  # Cardiología
        pulso = np.random.normal(100, 10, n)
        sistolica = np.random.normal(145, 10, n)
        diastolica = np.random.normal(90, 8, n)
        oxigeno = np.random.normal(96, 2, n)
        temperatura = np.random.normal(37.2, 0.3, n)
        creatinina = np.random.normal(1.0, 0.2, n)
        glucosa = np.random.normal(95, 10, n)

    elif categoria == 1:  # Neumología
        pulso = np.random.normal(80, 8, n)
        sistolica = np.random.normal(125, 10, n)
        diastolica = np.random.normal(80, 8, n)
        oxigeno = np.random.normal(88, 4, n)
        temperatura = np.random.normal(38.2, 0.4, n)
        creatinina = np.random.normal(0.9, 0.2, n)
        glucosa = np.random.normal(100, 10, n)

    elif categoria == 2:  # Nefrología
        pulso = np.random.normal(85, 10, n)
        sistolica = np.random.normal(135, 10, n)
        diastolica = np.random.normal(85, 8, n)
        oxigeno = np.random.normal(95, 2, n)
        temperatura = np.random.normal(37.0, 0.3, n)
        creatinina = np.random.normal(2.5, 0.5, n)  
        glucosa = np.random.normal(90, 10, n)

    elif categoria == 3:  # Endocrinología
        pulso = np.random.normal(90, 10, n)
        sistolica = np.random.normal(130, 10, n)
        diastolica = np.random.normal(82, 8, n)
        oxigeno = np.random.normal(97, 1.5, n)
        temperatura = np.random.normal(37.0, 0.2, n)
        creatinina = np.random.normal(1.0, 0.1, n)
        glucosa = np.random.normal(160, 25, n) 

    X = np.column_stack([pulso, sistolica, diastolica, oxigeno, temperatura, creatinina, glucosa])
    y = np.full(n, categoria)
    return X, y

# Crear dataset combinado
X_total, y_total = [], []
for cat in range(4):
    X, y = generar_datos(200, cat)
    X_total.append(X)
    y_total.append(y)

X = np.vstack(X_total)
y = np.hstack(y_total)

# Mostrar una muestra de los datos generados
columnas = ["Pulso", "Presión Sistólica", "Presión Diastólica", "Oxígeno", "Temperatura", "Creatinina", "Glucosa"]
df = pd.DataFrame(X, columns=columnas)
df["Categoría"] = y
categorias = ["Cardiología", "Neumología", "Nefrología", "Endocrinología"]
df["Categoría"] = df["Categoría"].apply(lambda i: categorias[i])

print("Ejemplo de datos generados (5 registros):\n")
print(df.head(), "\n")

# Entrenamiento del modelo
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
modelo = MLPClassifier(hidden_layer_sizes=(16, 8), max_iter=1500, random_state=42)
modelo.fit(X_train, y_train)

# Evaluación del modelo
y_pred = modelo.predict(X_test)
print("Precisión del modelo:", round(accuracy_score(y_test, y_pred) * 100, 2), "%\n")
print("Reporte de clasificación:\n")
print(classification_report(y_test, y_pred, target_names=categorias))


# Paciente Cardiologia
paciente_prueba = np.array([[95, 145, 88, 95, 37.3, 1.1, 100]])
# Paciente Neumologia
# paciente_prueba = np.array([[84, 128, 78, 90, 38.0, 1.0, 102]])
# Paciente Nefrologia
# paciente_prueba = np.array([[88, 133, 84, 94, 37.2, 2.3, 95]])
# Paciente Endocrinología
# paciente_prueba = np.array([[85, 125, 82, 94, 36.9, 1.3, 135]])

print("Datos del paciente ingresado:")
print(f"Pulso: {paciente_prueba[0][0]}")
print(f"Presión Sistólica: {paciente_prueba[0][1]}")
print(f"Presión Diastólica: {paciente_prueba[0][2]}")
print(f"Oxígeno: {paciente_prueba[0][3]}")
print(f"Temperatura: {paciente_prueba[0][4]}")
print(f"Creatinina: {paciente_prueba[0][5]}")
print(f"Glucosa: {paciente_prueba[0][6]}\n")

pred = modelo.predict(paciente_prueba)[0]
probabilidades = modelo.predict_proba(paciente_prueba)[0]

print("Resultado del diagnóstico:")
for i, cat in enumerate(categorias):
    print(f"{cat}: {probabilidades[i]*100:.2f}%")

print(f"\nDiagnóstico más probable: {categorias[pred]}")