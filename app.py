import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

# --- 1. FUNÇÕES MATEMÁTICAS PURAS (CORRIGIDAS) ---

def dist_2_points(x1, x2, y1, y2):
    return abs(math.sqrt((x2 - x1)**2 + (y2 - y1)**2))

def optimizar_k1999_real(center_line, inner_border, outer_border, iterations=3000, car_margin=0.5):
    """
    Otimiza a trajetória minimizando a distância total.
    car_margin: margem de segurança em metros (ex: 0.2m) para a roda não sair da pista.
    """
    opt_line = np.copy(center_line)
    n_points = len(center_line)
    
    # 1. Pré-calcular os limites seguros para cada waypoint
    safe_inner = np.zeros_like(inner_border)
    safe_outer = np.zeros_like(outer_border)
    
    for i in range(n_points):
        # Calcula o vetor direcional da borda interna para a externa
        w_vec = outer_border[i] - inner_border[i]
        w_len = np.linalg.norm(w_vec)
        w_dir = w_vec / w_len if w_len > 0 else np.array([0, 0])
        
        # Encolhe a pista virtualmente pela margem do carro
        safe_inner[i] = inner_border[i] + w_dir * car_margin
        safe_outer[i] = outer_border[i] - w_dir * car_margin

    # 2. Otimização Iterativa (O elástico real)
    for _ in range(iterations):
        temp_line = np.copy(opt_line)
        for i in range(n_points):
            prev_p = opt_line[i-1]
            next_p = opt_line[(i+1) % n_points]
            
            # O alvo ideal é exatamente o meio do caminho entre o ponto anterior e o próximo (Reta)
            target = (prev_p + next_p) / 2.0
            
            # Projeção do alvo na linha de limite seguro da pista
            A = safe_inner[i]
            B = safe_outer[i]
            
            AB = B - A
            AP = target - A
            
            # Produto escalar para achar o ponto mais próximo dentro da pista
            dot_product = np.dot(AP, AB)
            length_squared = np.dot(AB, AB)
            
            if length_squared == 0:
                t = 0
            else:
                t = dot_product / length_squared
                
            # Restringe 't' entre 0 e 1 para não sair da pista
            t = max(0.0, min(1.0, t))
            
            # Move o ponto para a nova posição otimizada
            temp_line[i] = A + t * AB
            
        opt_line = temp_line
        
    return opt_line

def calculate_radius(p1, p2, p3):
    a = dist_2_points(p1[0], p2[0], p1[1], p2[1])
    b = dist_2_points(p2[0], p3[0], p2[1], p3[1])
    c = dist_2_points(p3[0], p1[0], p3[1], p1[1])
    
    s = (a + b + c) / 2.0
    area_sq = s * (s - a) * (s - b) * (s - c)
    if area_sq <= 1e-10: 
        return 999.0
    
    area = math.sqrt(area_sq)
    return (a * b * c) / (4.0 * area)

def calculate_velocity_profile(opt_line, max_speed=4.0, min_speed=1.0, mu=0.7, gravity=9.81, lookahead=6):
    n_points = len(opt_line)
    v_ideal = np.zeros(n_points)
    
    # Passo 1: Velocidade Máxima de Curva (Aderência)
    for i in range(n_points):
        p1 = opt_line[i-1]
        p2 = opt_line[i]
        p3 = opt_line[(i+1) % n_points]
        radius = calculate_radius(p1, p2, p3)
        v_max_curve = math.sqrt(mu * gravity * radius)
        v_ideal[i] = min(max_speed, max(min_speed, v_max_curve))

    # Passo 2: Zonas de Frenagem (Lookahead - propagando para trás)
    v_profile = np.copy(v_ideal)
    for i in range(n_points):
        min_lookahead_speed = v_ideal[i]
        for j in range(1, lookahead + 1):
            idx = (i + j) % n_points
            if v_ideal[idx] < min_lookahead_speed:
                min_lookahead_speed = v_ideal[idx]
        
        # Freia com antecedência
        v_profile[i] = min(v_ideal[i], min_lookahead_speed * 1.3)
        
    # Passo 3: Zonas de Aceleração (Lookbehind - propagando para frente)
    v_final = np.copy(v_profile)
    max_acceleration_per_waypoint = 0.4  # Incremento máximo realista (m/s) por waypoint
    
    # Rodamos o loop 2 vezes para garantir que o último ponto conecte perfeitamente com o Ponto 0
    for _ in range(2):
        for i in range(n_points):
            prev_idx = i - 1 # Em Python, -1 pega o último elemento da lista
            
            # A velocidade limite do motor é a velocidade anterior + a taxa de aceleração
            motor_limit = v_final[prev_idx] + max_acceleration_per_waypoint
            
            # O carro escolhe o menor valor: ou o limite da física da curva, ou o limite do motor
            v_final[i] = min(v_profile[i], motor_limit)
            
            # Garante que não ultrapasse os limites globais
            v_final[i] = min(max_speed, max(min_speed, v_final[i]))

    return v_final

# --- 2. INTEGRAÇÃO E RENDERIZAÇÃO ---

# --- 2. INTEGRAÇÃO E RENDERIZAÇÃO ---

def processar_pista(track_data):
    center_line = track_data[:, 0:2]
    inner_border = track_data[:, 2:4]
    outer_border = track_data[:, 4:6]

    # Otimização K1999 (Modelo B) - AGORA COM PARÂMETROS AGRESSIVOS REAIS
    opt_line = optimizar_k1999_real(
        center_line, 
        inner_border, 
        outer_border, 
        iterations=10000,  # Elástico tensionado ao máximo
        car_margin=0.05    # Margem quase zero para lamber a zebra
    )
    
    v_ideal = calculate_velocity_profile(opt_line)

    # Monta a lista do Modelo B (K1999 + Velocidade Dinâmica)
    lista_k1999 = []
    for i in range(len(opt_line)):
        lista_k1999.append([round(float(opt_line[i][0]), 4), 
                            round(float(opt_line[i][1]), 4), 
                            round(float(v_ideal[i]), 2)])

    # Monta a lista do Modelo A (Centro Original + Velocidade Constante)
    lista_original = []
    velocidade_constante = 2.0 # Velocidade base segura para o modelo de controle
    for i in range(len(center_line)):
        lista_original.append([round(float(center_line[i][0]), 4), 
                               round(float(center_line[i][1]), 4), 
                               velocidade_constante])

    return center_line, inner_border, outer_border, opt_line, lista_k1999, lista_original


# --- INTERFACE WEB (STREAMLIT) ---
st.set_page_config(page_title="DeepRacer TCC - Otimizador Offline", layout="wide")
st.title("🏁 Pré-Processamento Offline - Trajetória Mais Curta")

arquivo_up = st.file_uploader("Escolha o arquivo da pista (.npy)", type=['npy'])

if arquivo_up is not None:
    track_data = np.load(arquivo_up)
    
    with st.spinner('Otimizando o elástico dentro das bordas...'):
        center, inner, outer, opt_line, lista_k1999, lista_original = processar_pista(track_data)

    st.success("Otimização concluída!")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(inner[:,0], inner[:,1], color='black', linewidth=1, label='Borda Interna')
    ax.plot(outer[:,0], outer[:,1], color='black', linewidth=1, label='Borda Externa')
    ax.plot(center[:,0], center[:,1], color='gray', linestyle='dashed', label='Centro Original')
    
    sc = ax.scatter(opt_line[:,0], opt_line[:,1], c=[p[2] for p in lista_k1999], 
                    cmap='RdYlGn', s=25, label='Linha Otimizada (Cor = Velocidade)')
    plt.colorbar(sc, label="Velocidade Ideal (m/s)")
    
    ax.set_aspect('equal')
    ax.legend(loc='lower right')
    st.pyplot(fig)

    # Exibe as duas listas lado a lado usando colunas do Streamlit
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Modelo A: Controle (Original)")
        st.write("Usa o centro da pista e velocidade constante de 2.0 m/s.")
        texto_original = "TRACK_DATA = [\n"
        for ponto in lista_original:
            texto_original += f"    {ponto},\n"
        texto_original += "]"
        st.code(texto_original, language='python')

    with col2:
        st.subheader("Modelo B: Proposto (K1999)")
        st.write("Usa a linha otimizada e velocidade calculada pela física.")
        texto_k1999 = "TRACK_DATA = [\n"
        for ponto in lista_k1999:
            texto_k1999 += f"    {ponto},\n"
        texto_k1999 += "]"
        st.code(texto_k1999, language='python')