import pandas as pd

class TrajectoryUnwrapper:
    """Desfazer as condições de contorno periódicas de trajetórias"""
    @staticmethod
    def unwrap_dataframe(df_particle: pd.DataFrame,L: int) -> pd.DataFrame:
        """
        Desfaz PBC para uma partícula individual
        
        Args:
            df_particle: DataFrame com colunas 'time','x','y'
            L: Tamanho da caixa
        
        Returns:
            DataFrame com colunas adicionais 'x_unwapped', 'y_unwrapped'
        """
        df_particle = df_particle.sort_values("time").copy()

        x_unwrapped = [df_particle["x"].iloc[0]] 
        y_unwrapped = [df_particle["y"].iloc[0]]

        for i in range(1, len(df_particle)):
            dx = df_particle["x"].iloc[i] - df_particle["x"].iloc[i-1]
            dy = df_particle["y"].iloc[i] - df_particle["y"].iloc[i-1]

            if dx > L/2:
                dx -= L
            elif dx < -L/2:
                dx += L
            
            if dy > L/2:
                dy -= L
            elif dy < -L /2:
                dy += L
            
            x_unwrapped.append(x_unwrapped[-1]+dx)
            y_unwrapped.append(y_unwrapped[-1]+dy)
        df_particle["x_unwrapped"] = x_unwrapped
        df_particle["y_unwrapped"] = y_unwrapped

        return df_particle

