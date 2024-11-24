import tensorflow as tf
from keras.utils import pad_sequences
import pandas as pd

# ------------------ Capas Personalizadas ------------------
class TransformerBlock(tf.keras.layers.Layer):
    def __init__(self, embed_dim, num_heads, ff_dim, rate=0.1):
        super(TransformerBlock, self).__init__()
        self.att = tf.keras.layers.MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)
        self.ffn = tf.keras.Sequential([tf.keras.layers.Dense(ff_dim, activation="relu"), tf.keras.layers.Dense(embed_dim)])
        self.layernorm1 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = tf.keras.layers.LayerNormalization(epsilon=1e-6)
        self.dropout1 = tf.keras.layers.Dropout(rate)
        self.dropout2 = tf.keras.layers.Dropout(rate)

    def call(self, inputs, training=False):
        attn_output = self.dropout1(self.att(inputs, inputs, training=training), training=training)
        out1 = self.layernorm1(inputs + attn_output)
        ffn_output = self.dropout2(self.ffn(out1, training=training), training=training)
        return self.layernorm2(out1 + ffn_output)


class TokenAndPositionEmbedding(tf.keras.layers.Layer):
    def __init__(self, maxlen, vocab_size, embed_dim):
        super(TokenAndPositionEmbedding, self).__init__()
        self.token_emb = tf.keras.layers.Embedding(input_dim=vocab_size, output_dim=embed_dim)
        self.pos_emb = tf.keras.layers.Embedding(input_dim=maxlen, output_dim=embed_dim)

    def call(self, x):
        positions = self.pos_emb(tf.range(start=0, limit=tf.shape(x)[-1]))
        return self.token_emb(x) + positions


# ------------------ Modelo Preentrenado ------------------
def cargar_modelo(ruta_modelo="/Users/alexlatorre/Documents/GitHub/local_ecityclic/ecityclic/model/modelo_transformer_tramites.h5"):
    """Carga el modelo Transformer preentrenado."""
    model = tf.keras.models.load_model(
        ruta_modelo,
        custom_objects={
            'TokenAndPositionEmbedding': TokenAndPositionEmbedding,
            'TransformerBlock': TransformerBlock
        }
    )
    return model


# ------------------ Función de Predicción ------------------
def predecir_tramite(raw_input_sequence, tramits_csv, max_seq_len, model):
    """
    Filtra trámites por 'Vigent=True' y realiza la predicción.
    raw_input_sequence: lista de trámites (secuencia de entrada).
    tramits_csv: Ruta al archivo tramits.csv.
    max_seq_len: Longitud máxima de la secuencia (padding).
    model: Modelo cargado con cargar_modelo.
    """
    tramits_df = pd.read_csv(tramits_csv)
    vigent_indices = tramits_df[tramits_df['Vigent'] == True].index.tolist()

    # Preparar el input
    input_sequence = pad_sequences([raw_input_sequence], maxlen=max_seq_len, padding='post', truncating='post')

    # Predicción
    predictions = model.predict(input_sequence)
    filtered_predictions = {idx: predictions[0][idx] for idx in vigent_indices}
    sorted_predictions = sorted(filtered_predictions.items(), key=lambda x: x[1], reverse=True)

    # Obtener las mejores predicciones
    top_10_predictions = sorted_predictions[:5]
    recommended_tramit, recommended_prob = top_10_predictions[0]

    return recommended_tramit, recommended_prob, top_10_predictions

def call_function(tramit_input):

    # Cargar el modelo preentrenado
    model = cargar_modelo("/Users/alexlatorre/Documents/GitHub/local_ecityclic/ecityclic/model/modelo_transformer_tramites.h5")

    # Realizar una predicción
    raw_input_sequence = tramit_input  # Entrada ejemplo
    tramits_csv = "/Users/alexlatorre/Documents/GitHub/local_ecityclic/data/tramits.csv"  # Ruta al archivo tramits.csv
    max_seq_len = 20  # Longitud máxima de secuencias

    # Realizar la predicción 
    recommended_tramit, _, top_10_predictions = predecir_tramite(
        raw_input_sequence, tramits_csv, max_seq_len, model
    )
    
    # Filtrar predicciones con probabilidad de al menos 2%
    filtered_predictions = [pred for pred in top_10_predictions if pred[1] >= 0.02]

    # Leer el archivo tramits.csv para obtener los títulos
    tramits_df = pd.read_csv(tramits_csv)
    
    # Obtener los títulos correspondientes a los índices de las predicciones filtradas
    top_10_titles = [tramits_df.loc[tramits_df['Sequence'] == idx, 'Titol'].values[0] for idx, _ in filtered_predictions]
    
    # Ver resultados
    if filtered_predictions:
        print(f"Trámite recomendado: {tramits_df.loc[tramits_df['Sequence'] == filtered_predictions[0][0], 'Titol'].values[0]}")
        print("\nTop predicciones con al menos 2% de probabilidad:")
        for title in top_10_titles:
            print(title)
    else:
        print("Trámite recomendado: Sol·licitud genèrica")
    
    return top_10_titles if filtered_predictions else ["Sol·licitud genèrica"]