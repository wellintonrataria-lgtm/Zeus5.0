# 🚀 Zeus 5.0 - Guia de Deploy Rápido

## ⚡ Deploy com 1 Clique

### Opção 1: Vercel (Recomendado - Mais Rápido)

1. **Acesse**: https://vercel.com
2. **Faça login** com GitHub/GitLab
3. **Importe o projeto**:
   - Clique em "New Project"
   - Conecte seu repositório GitHub
   - Ou faça upload do ZIP
4. **Configure**:
   - Framework Preset: "Other"
   - Build Command: `cd frontend && pnpm install && pnpm run build`
   - Output Directory: `frontend/dist`
5. **Deploy**: Clique em "Deploy"
6. **Pronto!** Seu link permanente estará disponível

### Opção 2: Render (Alternativa Gratuita)

1. **Acesse**: https://render.com
2. **Crie conta** gratuita
3. **Novo Web Service**:
   - Conecte repositório GitHub
   - Ou faça upload do código
4. **Configurações**:
   - Environment: `Node`
   - Build Command: `cd frontend && npm install -g pnpm && pnpm install && pnpm run build`
   - Start Command: `cd backend && pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Deploy automático** será iniciado
6. **Link permanente** gerado automaticamente

### Opção 3: Netlify (Só Frontend)

1. **Acesse**: https://netlify.com
2. **Arraste a pasta** `frontend/dist` (após build)
3. **Deploy instantâneo**
4. **Configure backend** separadamente

## 🔧 Deploy Local/VPS

### Docker (Recomendado)
```bash
# Clone/extraia o projeto
cd zeus-5.0

# Inicie tudo com Docker
docker-compose up -d

# Acesse:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### Manual
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend (nova aba)
cd frontend
pnpm install
pnpm run build
pnpm run preview --port 3000
```

## 🌐 URLs de Exemplo

Após o deploy, você terá:
- **Frontend**: `https://seu-app.vercel.app`
- **Backend**: `https://seu-app.vercel.app/api`
- **Docs**: `https://seu-app.vercel.app/api/docs`

## ⚙️ Configurações Importantes

### Variáveis de Ambiente (se necessário)
```bash
# No painel do Vercel/Render
PYTHONPATH=backend
REACT_APP_API_URL=https://seu-backend-url.com
```

### CORS (já configurado)
O backend já está configurado para aceitar requisições do frontend.

## 🔍 Verificação Pós-Deploy

1. **Acesse o frontend** - deve carregar a interface
2. **Teste a API** - vá para `/api/docs`
3. **Verifique sinais** - clique em "Atualizar" no dashboard
4. **WebSocket** - sinais devem atualizar automaticamente

## 🆘 Solução de Problemas

### Erro de Build
- Verifique se todas as dependências estão no `requirements.txt`
- Certifique-se que o Node.js é versão 18+

### API não responde
- Verifique se o backend foi deployado corretamente
- Confirme as URLs da API no frontend

### Frontend não carrega
- Verifique se o build foi executado
- Confirme se os arquivos estão na pasta `dist`

## 📞 Suporte

- **Documentação**: README.md completo
- **Issues**: Use o GitHub Issues
- **Logs**: Disponíveis no painel do Vercel/Render

---

**🎯 Resultado Final**: Robô de trading Zeus 5.0 funcionando 24/7 com link permanente!

**⏱️ Tempo estimado**: 5-10 minutos para deploy completo

