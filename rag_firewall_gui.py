import tkinter as tk
from tkinter import scrolledtext, messagebox
import chromadb
import requests
import uuid
from groq import Groq
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FIREWALL_URL = "http://127.0.0.1:8000/verify"

# --- Initialize Systems ---
# 1. Connect to the Live LLM
groq_client = Groq(api_key=GROQ_API_KEY)

# 2. Connect to the Permanent Local Database
chroma_client = chromadb.PersistentClient(path="./my_local_brain_v3")
collection = chroma_client.get_or_create_collection(name="engineering_portfolio")

class RAGFirewallApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Enterprise AI Firewall - RAG Gateway")
        self.root.geometry("900x550")
        
        # Configure Split Screen (Grid)
        self.root.columnconfigure(0, weight=1) # Left Panel (Memory)
        self.root.columnconfigure(1, weight=2) # Right Panel (Chat/Report)
        self.root.rowconfigure(0, weight=1)
        
        self.build_ingestion_panel()
        self.build_chat_panel()

    def build_ingestion_panel(self):
        '''Zone 1: Manual Memory Storage'''
        left_frame = tk.Frame(self.root, bg="#1e272e", padx=20, pady=20)
        left_frame.grid(row=0, column=0, sticky="nsew")
        
        tk.Label(left_frame, text="🗄️ Store New Memory", fg="#00d2d3", bg="#1e272e", font=("Segoe UI", 16, "bold")).pack(pady=(0, 15))
        
        tk.Label(left_frame, text="Type a fact you want the AI to remember:", fg="#c8d6e5", bg="#1e272e", font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 5))
        
        self.memory_input = scrolledtext.ScrolledText(left_frame, height=12, wrap=tk.WORD, font=("Consolas", 11), bg="#2f3542", fg="white", insertbackground="white")
        self.memory_input.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        save_btn = tk.Button(left_frame, text="Vectorize & Save to DB", bg="#1dd1a1", fg="black", font=("Segoe UI", 12, "bold"), relief="flat", cursor="hand2", command=self.save_memory)
        save_btn.pack(fill=tk.X, pady=5)
        
        tk.Label(left_frame, text="Data is stored permanently in ./my_local_brain", fg="#576574", bg="#1e272e", font=("Segoe UI", 8)).pack(side=tk.BOTTOM, pady=10)

    def build_chat_panel(self):
        '''Zone 2: Ask Questions & Get the Firewall Report'''
        right_frame = tk.Frame(self.root, bg="#f5f6fa", padx=20, pady=20)
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        tk.Label(right_frame, text="🛡️ Ask LLM (Firewall Protected)", fg="#2f3640", bg="#f5f6fa", font=("Segoe UI", 16, "bold")).pack(pady=(0, 15))
        
        # Chat Report Window
        self.chat_display = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, font=("Segoe UI", 11), state=tk.DISABLED, bg="white", relief="flat")
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Color tags for the report
        self.chat_display.tag_config("user", foreground="#2980b9", font=("Segoe UI", 11, "bold"))
        self.chat_display.tag_config("safe", foreground="#27ae60")
        self.chat_display.tag_config("blocked", foreground="#c0392b", font=("Segoe UI", 11, "bold"))
        self.chat_display.tag_config("system", foreground="#7f8c8d", font=("Segoe UI", 10, "italic"))
        
        # Input Area
        input_frame = tk.Frame(right_frame, bg="#f5f6fa")
        input_frame.pack(fill=tk.X)
        
        self.query_input = tk.Entry(input_frame, font=("Segoe UI", 12), relief="solid", bd=1)
        self.query_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))
        
        # Allow pressing Enter to send
        self.query_input.bind("<Return>", lambda event: self.process_query())
        
        ask_btn = tk.Button(input_frame, text="Submit Query", bg="#2e86de", fg="white", font=("Segoe UI", 12, "bold"), relief="flat", cursor="hand2", command=self.process_query)
        ask_btn.pack(side=tk.RIGHT, ipadx=10, ipady=4)

    def append_chat(self, text, tag):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, text + "\n\n", tag)
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def save_memory(self):
        memory_text = self.memory_input.get("1.0", tk.END).strip()
        if not memory_text:
            return
            
        memory_id = "mem_" + str(uuid.uuid4())[:8]
        collection.upsert(documents=[memory_text], ids=[memory_id])
        
        self.memory_input.delete("1.0", tk.END)
        messagebox.showinfo("Memory Saved", "Success! This fact is now permanently embedded in your ChromaDB vector store.")
        self.append_chat(f"🗄️ System: New memory ingested -> '{memory_text}'", "system")

    def process_query(self):
        query = self.query_input.get().strip()
        if not query:
            return
            
        self.query_input.delete(0, tk.END)
        self.append_chat(f"👤 You: {query}", "user")
        self.root.update() 
        
        try:
            # 1. RAG Retrieval (Increased n_results to grab multiple memories)
            results = collection.query(query_texts=[query], n_results=3)
            
            if not results['documents'] or not results['documents'][0]:
                self.append_chat("🤖 System: I don't have any memories related to that query.", "system")
                return
                
            # Stitch all retrieved vectors together into one combined string
            retrieved_docs = results['documents'][0]
            retrieved_context = " | ".join(retrieved_docs)
            
            self.append_chat(f"🔍 Retrieved Context: {retrieved_context}", "system")
            self.root.update()
            
            # 2. LLM Generation
            system_prompt = f"""
                                You are a strict data-retrieval assistant. Answer based ONLY on the context: '{retrieved_context}'
    
                                CRITICAL RULES:
                                1. Answer in complete sentences.
                                2. NEVER invent policies, entities, or jargon not found in the text.NEVER speculate, guess, or use words like "likely", "assume", or "probably".
                                3. THE GOLDEN RULE: If the user asks for something that violates the context (like taking 35 days when the limit is 30), DO NOT repeat their false number in your answer. Simply state the actual rule from the context.
                                4. THE BLINDSPOT RULE: If the context does not contain the answer, write a natural, nuanced sentence explaining exactly what information is missing from the text. You MUST append the exact tag [MISSING_CONTEXT] at the very end of your response.

                                EXAMPLE OF RULE 4:
                                Question: Was the outage caused by the 50% CPU?
                                Context: The system fails if CPU is over 40%.
                                Answer: The system fails if CPU is over 40%, but the actual cause of the outage is not specified. [MISSING_CONTEXT]
                                """


                              
                        
            
            
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.2 
            )
           

            # 3. Parse the LLM's Answer
            llm_answer = chat_completion.choices[0].message.content.strip()
            
            # --- THE STEALTH KEYWORD INTERCEPTOR ---
            if "[MISSING_CONTEXT]" in llm_answer:
                # 1. Clean the tag out so the user never sees it
                clean_answer = llm_answer.replace("[MISSING_CONTEXT]", "").strip()
                
                # 2. Display the beautiful, nuanced response safely
                self.append_chat(f"🛡️ FIREWALL BYPASSED (No Data)\n🤖 AI: {clean_answer}", "safe")
                return # Exit before DeBERTa gets confused
            
            # 4. Firewall Validation (Only runs if the AI actually generated a real answer)
            payload = {
                "question": query,          # This must be included!
                "premise": retrieved_context,
                "hypothesis": llm_answer
            }
            response = requests.post(FIREWALL_URL, json=payload)
            decision = response.json()
            
            confidence = decision.get('confidence_score', 0) * 100
            
            # 5. Generate the Report
            if decision.get("is_safe"):
                self.append_chat(f"✅ FIREWALL PASSED (Confidence: {confidence:.1f}%)\n🤖 AI: {llm_answer}", "safe")
            else:
                self.append_chat(f"❌ FIREWALL BLOCKED (Confidence: {confidence:.1f}%)\n⚠️ AI Hallucination Intercepted! The AI tried to say:\n'{llm_answer}'", "blocked")

        except Exception as e:
            self.append_chat(f"⚠️ Error: {str(e)}", "blocked")
if __name__ == "__main__":
    root = tk.Tk()
    app = RAGFirewallApp(root)
    root.mainloop()
