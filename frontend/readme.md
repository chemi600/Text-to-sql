# Text-to-SQL
**Enlace GitHub:** https://github.com/chemi600/Text-to-sql

## Integrantes
- **Raúl Mateo**
- **Samuel Salcedo**

---

## Descripción

**Text-to-SQL** es una aplicación basada en Inteligencia Artificial capaz de **convertir lenguaje natural en consultas SQL**.

El objetivo de la aplicación es permitir que usuarios sin conocimientos avanzados de bases de datos puedan **consultar información utilizando frases normales**, por ejemplo:

> "Muéstrame todos los clientes que realizaron pedidos en 2023"

La aplicación traduce automáticamente esa petición a una consulta SQL equivalente:

```sql
SELECT *
FROM clientes
WHERE año_pedido = 2023;
```
## Modelo base
El modelo base utilizado es **Qwen2.5-Coder-1.5B**, disponible en Hugging Face.

Elegimos este modelo por varias razones:

Buen rendimiento en tareas de generación de texto y código

- Arquitectura moderna y eficiente

- Buen equilibrio entre capacidad del modelo y recursos computacionales

- Integración sencilla con el ecosistema de Hugging Face Transformers

Además, su capacidad para comprender instrucciones en lenguaje natural lo hace adecuado para tareas de traducción semántica, como transformar texto en consultas SQL.

## Tecnica de Adaptación
Para adaptar el modelo a nuestra tarea utilizamos **LoRA (Low-Rank Adaptation)**.

**¿Por qué elegimos LoRA?**
Elegimos LoRA porque permite ajustar modelos grandes de forma eficiente sin necesidad de reentrenar todos los parámetros del modelo.

Sus principales ventajas son:

- Reduce el consumo de memoria

- Disminuye el tiempo de entrenamiento

- Permite reutilizar el modelo base sin modificarlo completamente

Esto lo convierte en una técnica muy utilizada cuando se trabaja con Large Language Models (LLMs).

**¿Como funciona LoRA?**

LoRA introduce pequeñas matrices entrenables de bajo rango dentro de determinadas capas del modelo, generalmente en las capas de atención.

En lugar de actualizar todos los pesos del modelo:

1. El modelo base permanece congelado.

2. Se añaden pequeños módulos entrenables.

3. Solo se entrenan esos nuevos parámetros.

De esta forma, el modelo puede adaptarse a nuevas tareas utilizando menos recursos computacionales.

## Dataset

Escogimos este dataset de sql que se encuentra en Huggin Face
https://huggingface.co/datasets/b-mc2/sql-create-context
Para este dataset no procesamos ningun dato.

## Instalación y Ejecución Rápida 

1. Navega hasta la carpeta raíz del proyecto en tu terminal (donde se encuentra el archivo `docker-compose.yml`).
2. Ejecuta el siguiente comando para construir y levantar toda la arquitectura:

   ```bash
   docker-compose up --build -d
   ```

3. **¡Importante! La primera vez que ejecutes esto:** El backend tiene que descargar el "Cerebro Base" de la IA (`Qwen/Qwen2.5-Coder-1.5B`) desde los servidores de HuggingFace (Aprox. 3 GB de peso). Todo es automático, pero dependiendo de tu velocidad de internet, tardará algunos minutos. El Frontend te avisará amigablemente cuando esté listo.

4. Accede a las aplicaciones desde tu navegador web:
   - **Aplicación Web (Streamlit):** [http://localhost:8501](http://localhost:8501)
   - **Documentación de la API (FastAPI Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)


## Ejemplos de Prueba
Una vez que el Frontend esté listo en `http://localhost:8501`, puedes copiar y pegar estos ejemplos para interactuar con la IA:

**Prueba Fácil:**
- **Pregunta:** Dame los nombres de todos los empleados
- **Contexto:** `CREATE TABLE empleados (id INT, nombre VARCHAR, departamento VARCHAR);`
- **Respuesta:** `SELECT nombre FROM empleados ORDER BY id DESC LIMIT 10`

**Prueba Intermedia (Agrupación):**
- **Pregunta:** ¿Cuántas ventas tiene cada tienda ordenado de mayor a menor?
- **Contexto:** `CREATE TABLE ventas (id INT, tienda_id INT, monto DECIMAL); CREATE TABLE tiendas (id INT, nombre VARCHAR);`
- **Respuesta:** `SELECT COUNT(*), t1.nombre FROM tiendas AS t1 JOIN ventas AS t2 ON t1.id = t2.tienda_id GROUP BY t1.nombre ORDER BY COUNT(*) DESC`

## Referencias
- https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B


## Autoevalución

**¿Qué fue lo más difícil?**

Uno de los principales desafíos fue:

- Preparar y estructurar correctamente el dataset de entrenamiento

- Ajustar los prompts para mejorar la generación de consultas SQL


También fue complicado encontrar el equilibrio entre precisión y generalización del modelo.

**¿Qué resultados obtuvimos?**

Los resultados obtenidos fueron positivos:

- El modelo es capaz de traducir muchas consultas en lenguaje natural a SQL

- Funciona especialmente bien con consultas simples y de complejidad media


Sin embargo, en consultas más complejas (como múltiples JOIN o subconsultas, vistas) todavía puede cometer errores.

**¿Qué mejoraríamos con más tiempo?**

Si tuviéramos más tiempo, nos gustaría:

- Entrenar el modelo con un dataset más grande y variado

- Implementar un sistema de validación automática de consultas SQL

- Evaluar el modelo con consultas más complejas
