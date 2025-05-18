import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status
import requests
from bs4 import BeautifulSoup

# JWT設定
SECRET_KEY = "your-secret-key"  # 本番環境では安全な方法で管理してください
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class CompanyAnalysisAgent:
    def __init__(self):
        self.name = "company_analysis_agent"
        self.description = "An agent that performs company analysis using web search results"
        self.version = "0.1.0"
        self.users = {}  # 簡易的なユーザー管理（本番環境ではDBを使用）

    def get_agent_card(self) -> Dict:
        """A2Aプロトコルに準拠したエージェントカードを返す"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "auth": {
                "type": "bearer",
                "description": "JWT token based authentication"
            },
            "skills": [
                {
                    "name": "analyze_company",
                    "description": "Analyze a company using web search results",
                    "parameters": {
                        "company_name": {
                            "type": "string",
                            "description": "Name of the company to analyze"
                        }
                    }
                }
            ]
        }

    def create_access_token(self, data: dict) -> str:
        """JWTトークンを生成する"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(self, token: str) -> Dict:
        """JWTトークンを検証する"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials"
                )
            return {"username": username}
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

    def register_user(self, username: str, password: str) -> Dict:
        """ユーザーを登録する（簡易的な実装）"""
        if username in self.users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        self.users[username] = password
        access_token = self.create_access_token({"sub": username})
        return {"access_token": access_token, "token_type": "bearer"}

    def authenticate_user(self, username: str, password: str) -> Dict:
        """ユーザーを認証する"""
        if username not in self.users or self.users[username] != password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        access_token = self.create_access_token({"sub": username})
        return {"access_token": access_token, "token_type": "bearer"}

    def analyze_company(self, company_name: str) -> Dict:
        """企業分析を実行する"""
        # Web検索を実行して企業情報を収集
        search_results = self._search_company_info(company_name)

        # 収集した情報を分析
        analysis = self._analyze_search_results(search_results)

        return {
            "company_name": company_name,
            "analysis": analysis,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _search_company_info(self, company_name: str) -> List[Dict]:
        """企業情報をWeb検索で収集する"""
        # ここでは簡易的な実装。実際の実装では適切なAPI（Google Custom Search等）を使用
        search_results = []
        try:
            # 検索URLの例（実際の実装では適切なAPIを使用）
            url = f"https://www.google.com/search?q={company_name}+company+information"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            # 検索結果から情報を抽出（実装例）
            for result in soup.find_all("div", class_="g"):
                title = result.find("h3")
                snippet = result.find("div", class_="VwiC3b")
                if title and snippet:
                    search_results.append({
                        "title": title.text,
                        "snippet": snippet.text
                    })
        except Exception as e:
            print(f"Error during web search: {e}")

        return search_results

    def _analyze_search_results(self, search_results: List[Dict]) -> Dict:
        """検索結果を分析して構造化された分析結果を返す"""
        # 実際の実装ではより高度な分析ロジックを実装
        analysis = {
            "overview": "",
            "key_points": [],
            "industry": "",
            "competitors": [],
            "recent_news": []
        }

        for result in search_results:
            # ここで検索結果を分析し、適切なカテゴリに情報を振り分け
            snippet = result.get("snippet", "")
            title = result.get("title", "")

            # 簡易的な分析ロジック
            if "overview" in title.lower():
                analysis["overview"] = snippet
            elif "industry" in title.lower():
                analysis["industry"] = snippet
            elif "competitor" in title.lower():
                analysis["competitors"].append(snippet)
            elif "news" in title.lower():
                analysis["recent_news"].append({
                    "title": title,
                    "summary": snippet
                })

        return analysis