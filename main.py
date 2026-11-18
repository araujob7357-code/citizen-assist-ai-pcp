"""
CitizenTech - Alerta Inteligente de Enchentes (Raspberry Pi Pico + MicroPython)
Computer Organization and Architecture - GS2026.2

Problema: enchentes urbanas pegam a populacao de surpresa; alertas baseados so
em "nivel acima de X" chegam tarde demais.

Solucao: a Pico le (1) o nivel do rio/corrego por sensor ultrassonico e
(2) a intensidade da chuva por ADC (potenciometro simulando pluviometro).
Alem do nivel, calcula a TAXA DE SUBIDA da agua (cm/min) e estima quanto
tempo falta para a cota critica. Sinaliza com LEDs e buzzer.

Conexao com a disciplina:
- GPIO: saidas (LEDs/buzzer/TRIG) e entradas (ECHO/botao) via registradores
- ADC de 12 bits (lido como 16 bits): conversao analogico -> digital
- Timer de hardware: amostragem periodica sem bloquear a CPU
- Interrupcao (IRQ): botao "silenciar alarme" tratado por evento
- Medida de tempo em microssegundos para calcular distancia (ultrassom)

Escala da simulacao: 1 amostra (1 s real) = 1 minuto de tempo "do mundo real".
"""
from machine import Pin, ADC, Timer, time_pulse_us
import time

# ---------------- Pinos ----------------
TRIG = Pin(3, Pin.OUT)
ECHO = Pin(2, Pin.IN)
LED_VERDE = Pin(13, Pin.OUT)
LED_AMARELO = Pin(14, Pin.OUT)
LED_VERMELHO = Pin(15, Pin.OUT)
BUZZER = Pin(12, Pin.OUT)
BOTAO = Pin(16, Pin.IN, Pin.PULL_UP)
CHUVA = ADC(26)  # GP26 = ADC0 (potenciometro = pluviometro)

# ---------------- Parametros ----------------
ALTURA_SENSOR_CM = 100     # distancia do sensor ate o leito do rio (seco)
COTA_ATENCAO_CM = 40       # nivel da agua que exige atencao
COTA_CRITICA_CM = 70       # nivel de transbordamento iminente
TAXA_ALERTA = 2.0          # cm/min -> subida rapida
TAXA_EMERGENCIA = 4.0      # cm/min -> subida muito rapida
CHUVA_FORTE_MMH = 60       # mm/h considerada chuva forte
CHUVA_MAX_MMH = 100        # fundo de escala do potenciometro
JANELA = 5                 # amostras usadas para calcular a taxa
INTERVALO_MS = 1000        # periodo de amostragem (1 s = 1 min simulado)

# ---------------- Estado (alterado em IRQ/Timer) ----------------
alarme_silenciado = False
ler_agora = False
ultimo_botao_ms = 0
historico = []  # ultimos niveis (cm)


def medir_distancia_cm():
    """Pulso de 10 us no TRIG; mede a duracao do ECHO."""
    TRIG.low()
    time.sleep_us(2)
    TRIG.high()
    time.sleep_us(10)
    TRIG.low()
    duracao = time_pulse_us(ECHO, 1, 30000)  # timeout 30 ms
    if duracao < 0:
        return None
    # som ~ 0.0343 cm/us; ida e volta -> divide por 2
    return duracao * 0.0343 / 2


def ler_chuva_mmh():
    """Media de 8 leituras do ADC (16 bits) -> mm/h."""
    soma = 0
    for _ in range(8):
        soma += CHUVA.read_u16()
    media = soma / 8
    return media / 65535 * CHUVA_MAX_MMH


def calcular_taxa(nivel):
    """Taxa de subida em cm/min usando a janela de amostras."""
    historico.append(nivel)
    if len(historico) > JANELA:
        historico.pop(0)
    if len(historico) < 2:
        return 0.0
    return (historico[-1] - historico[0]) / (len(historico) - 1)  # cm por amostra = cm/min


def definir_leds(verde, amarelo, vermelho):
    LED_VERDE.value(verde)
    LED_AMARELO.value(amarelo)
    LED_VERMELHO.value(vermelho)


def bip(vezes, dur_ms=100):
    for _ in range(vezes):
        BUZZER.high()
        time.sleep_ms(dur_ms)
        BUZZER.low()
        time.sleep_ms(dur_ms)


def classificar(nivel, taxa, chuva):
    """Retorna 'NORMAL', 'ALERTA' ou 'EMERGENCIA'."""
    if nivel >= COTA_CRITICA_CM or (nivel >= COTA_ATENCAO_CM and taxa >= TAXA_EMERGENCIA):
        return "EMERGENCIA"
    if nivel >= COTA_ATENCAO_CM or taxa >= TAXA_ALERTA or (chuva >= CHUVA_FORTE_MMH and nivel >= 20):
        return "ALERTA"
    return "NORMAL"


# ---------------- Interrupcao do botao ----------------
def botao_irq(pin):
    global alarme_silenciado, ultimo_botao_ms
    agora = time.ticks_ms()
    if time.ticks_diff(agora, ultimo_botao_ms) > 250:  # debounce
        ultimo_botao_ms = agora
        alarme_silenciado = True


BOTAO.irq(trigger=Pin.IRQ_FALLING, handler=botao_irq)


# ---------------- Timer periodico ----------------
def timer_cb(t):
    global ler_agora
    ler_agora = True


Timer(period=INTERVALO_MS, mode=Timer.PERIODIC, callback=timer_cb)

# ---------------- Programa principal ----------------
print("Alerta Inteligente de Enchentes - CitizenTech - iniciado")
definir_leds(1, 1, 1)
time.sleep_ms(500)
definir_leds(0, 0, 0)

estado_anterior = None

while True:
    if ler_agora:
        ler_agora = False

        dist = medir_distancia_cm()
        if dist is None:
            print("Erro de leitura do sensor ultrassonico")
            continue

        nivel = max(0.0, min(ALTURA_SENSOR_CM, ALTURA_SENSOR_CM - dist))  # altura da agua (cm)
        chuva = ler_chuva_mmh()
        taxa = calcular_taxa(nivel)
        estado = classificar(nivel, taxa, chuva)

        # Previsao: minutos ate a cota critica, se a agua esta subindo
        previsao = None
        if taxa > 0.1 and nivel < COTA_CRITICA_CM:
            previsao = (COTA_CRITICA_CM - nivel) / taxa

        # Saidas
        if estado == "EMERGENCIA":
            definir_leds(0, 0, 1)
            if not alarme_silenciado:
                bip(3, 80)
        elif estado == "ALERTA":
            definir_leds(0, 1, 0)
            if not alarme_silenciado:
                bip(1, 200)
        else:
            definir_leds(1, 0, 0)
            alarme_silenciado = False  # situacao normalizada -> rearma

        # Telemetria (simula envio IoT para a Defesa Civil)
        linha = "nivel={:.0f}cm | chuva={:.0f}mm/h | taxa={:+.1f}cm/min | {}".format(
            nivel, chuva, taxa, estado)
        if previsao is not None:
            linha += " | cota critica em ~{:.0f} min".format(previsao)
        if alarme_silenciado:
            linha += " | (alarme silenciado)"
        print(linha)

        if estado != estado_anterior and estado == "EMERGENCIA":
            print(">>> EMERGENCIA: notificar Defesa Civil e acionar sirene!")
        estado_anterior = estado

    time.sleep_ms(10)
