# Introduction

Arivu is a retrieval augmented generation platform built to demonstrate production-grade RAG architecture.

# Architecture

The system uses hybrid retrieval combining dense vector search with BM25 keyword matching, followed by cross-encoder reranking to select the most relevant passages before generation.
