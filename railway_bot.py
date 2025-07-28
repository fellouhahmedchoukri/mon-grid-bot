import os
import time
import ccxt
from flask import Flask, request

app = Flask(__name__)

# Configuration
CONFIG = {
    "exchange": "binance",
    "symbol": "BTC/USDT",
    "capital": 100,
    "high_price": 70000,
    "low_price": 60000,
    "stop_level": 59000
}

def run_strategy():
    try:
        print("🚀 Démarrage de la stratégie Grid Trading...")
        
        # Connexion à Binance
        exchange = ccxt.binance({
            'apiKey': os.getenv('BINANCE_API_KEY'),
            'secret': os.getenv('BINANCE_API_SECRET'),
            'options': {'adjustForTimeDifference': True}
        })
        exchange.set_sandbox_mode(True)  # Mode test activé
        
        # Charger les marchés
        exchange.load_markets()
        print(f"✅ Marchés chargés: {len(exchange.markets)} pairs")
        
        # Calcul des niveaux de grille
        grid_range = CONFIG['high_price'] - CONFIG['low_price']
        grid_levels = 10
        grid_factor = grid_range / (grid_levels - 1)
        grid_prices = [CONFIG['high_price'] - i * grid_factor for i in range(grid_levels)]
        print(f"🔢 Niveaux de grille: {grid_prices}")
        
        # Placement des ordres
        for i, price in enumerate(grid_prices[5:]):
            try:
                # Calcul du montant
                amount = CONFIG['capital'] * 0.2 / price
                
                # Placer l'ordre
                order = exchange.create_limit_buy_order(
                    symbol=CONFIG['symbol'],
                    amount=amount,
                    price=price
                )
                print(f"✅ Ordre #{i+1} placé à {price}$: ID {order['id']}")
                
            except ccxt.InsufficientFunds:
                print(f"❌ Fonds insuffisants pour l'ordre à {price}$")
            except ccxt.NetworkError as e:
                print(f"❌ Erreur réseau: {e}")
            except Exception as e:
                print(f"❌ Erreur inattendue: {e}")
        
        print("🎯 Stratégie exécutée avec succès!")
        
    except Exception as e:
        print(f"🔥 ERREUR CRITIQUE: {str(e)}")
        import traceback
        traceback.print_exc()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(f"📨 Webhook reçu: {data}")
    
    if data.get('secret') != os.getenv('WEBHOOK_SECRET'):
        return "Accès refusé", 403
    
    run_strategy()
    return "Stratégie exécutée!", 200

@app.route('/')
def home():
    return "🤖 Bot Grid Trading Opérationnel"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
