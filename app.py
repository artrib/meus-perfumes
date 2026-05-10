if not result.empty:
            csv = result.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Descarregar resultados (CSV)", csv, "meus_perfumes.csv", "text/csv")

            # --- GRÁFICO DE COLUNAS NO FINAL ---
            st.markdown("---")
            st.subheader("📊 Quantidade por Estação do Ano")
            
            # Contagem dos dados filtrados
            contagem = result["Estações do Ano"].value_counts().reset_index()
            contagem.columns = ["Estação", "Quantidade"]
            
            # Ordenar para o gráfico ficar mais bonito (opcional)
            contagem = contagem.sort_values(by="Quantidade", ascending=False)
            
            if not contagem.empty:
                # Criar o gráfico de colunas (bar)
                fig = px.bar(
                    contagem, 
                    x="Estação", 
                    y="Quantidade",
                    text="Quantidade", # Mostra o número em cima da barra
                    color="Estação",   # Cores diferentes por barra
                    color_discrete_sequence=px.colors.qualitative.Safe
                )
                
                # Ajustes de design
                fig.update_traces(textposition='outside') # Coloca o número fora da barra
                fig.update_layout(
                    showlegend=False,
                    xaxis_title="Estações",
                    yaxis_title="Nº de Perfumes",
                    margin=dict(t=20, b=20, l=0, r=0),
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
