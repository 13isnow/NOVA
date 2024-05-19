import chromadb
from text2vec import SentenceModel
import pandas


class VectorModel:

    def __init__(self, model_path: str = "BAAI/bge-small-zh-v1.5"):
        self.model = SentenceModel(model_path)


class Embedding:

    def __init__(
            self,
            csv_path: str,  # csv_path: 单列数据的 csv 文件
            col_name: str,  # col_name: csv 文件中的列名
            source_name: str,  # source_name: 当前 csv 文件数据的来源
            batch_size: int  # batch_size: 文本转换为向量的批次，即每次转换的数量
    ):
        self.vectors = None
        self.sentences = pandas.read_csv(csv_path)[col_name].tolist()
        self.batch_size = batch_size
        self.source_name = source_name
        self.num_batches = (len(self.sentences) + batch_size - 1) // batch_size

    def get_embeddings(
            self,
            model: VectorModel,  # 使用的模型
    ):
        results = []
        for i in range(self.num_batches):
            start_index = i * self.batch_size
            end_index = min((i + 1) * self.batch_size, len(self.sentences))
            sentence_batch = self.sentences[start_index:end_index]  # 获取当前批次的文本
            batch_embeddings = model.model.encode(sentence_batch)  # 转换当前批次的文本为向量
            results.extend(batch_embeddings)  # 将转换结果添加到列表中
        results = [embedding.tolist() for embedding in results]
        self.vectors = results


class VectorDatabase:

    def __init__(
            self,
            db_path: str,  # db_path: 向量数据库的路径
            collection_name: str,  # collection_name: 向量数据库下的集合名
    ):
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name)

    def get_similar_sentences(
            self,
            model: VectorModel,  # 使用的模型
            query_texts: str,  # query_texts: 单条待查询的句子
            n_results: int = 3  # n_results: 需要查询的相似句子数量
    ):
        query_embeddings = [embedding.tolist() for embedding in model.model.encode([query_texts])]
        results = self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results
        )
        return results

    def create_db(
            self,
            vectors: Embedding
    ):
        ids = [f"id{i}" for i in range(len(vectors.sentences))]
        for i in range(vectors.num_batches):
            start_index = i * vectors.batch_size
            end_index = min((i + 1) * vectors.batch_size, len(vectors.sentences))
            batch_vectors = vectors.vectors[start_index:end_index]
            batch_sentences = vectors.sentences[start_index:end_index]
            meta_datas = [{"source": vectors.source_name} for _ in range(len(batch_sentences))]
            batch_ids = ids[start_index:end_index]
            self.collection.add(
                embeddings=batch_vectors,
                documents=batch_sentences,
                metadatas=meta_datas,
                ids=batch_ids,
            )


if __name__ == '__main__':
    model = VectorModel(model_path="BAAI/bge-small-zh-v1.5")
    database = VectorDatabase(db_path="demo", collection_name="20230915")
    vector = Embedding(
        csv_path="sentence.csv",
        col_name="2023年南京大学本科教育九大关键词",
        source_name="官方网页",
        batch_size=3
    )
    vector.get_embeddings(model)
    database.create_db(vector)

    similarity = database.get_similar_sentences(
        model,
        query_texts="队伍展新貌",
        n_results=2
    )
    print(similarity)
