from qdrant_client import QdrantClient
import time

client = QdrantClient(
    url='https://815fe83f-3b7e-405c-bf7c-32adc230d84d.eu-central-1-0.aws.cloud.qdrant.io',
    api_key='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.W_1tkCi9FtpldKY5Y2CkB3HqswhxkFbTMV8lgfAvAhE',
    timeout=60
)

print('Testing Qdrant connection...')

try:
    # Get collection info
    collection_info = client.get_collection('documents')
    print(f'✅ Collection exists')
    print(f'   Points count: {collection_info.points_count}')
    print(f'   Vectors count: {collection_info.vectors_count}')
    
    # Try to scroll some points
    print('\nTrying to fetch points...')
    start_time = time.time()
    scroll_result = client.scroll(
        collection_name='documents',
        limit=5,
        with_payload=True,
        with_vectors=False
    )
    end_time = time.time()
    
    print(f'✅ Scroll took {end_time - start_time:.2f}s')
    print(f'   Retrieved {len(scroll_result[0])} points')
    
    # Try a query
    if collection_info.points_count > 0:
        print('\nTrying query_points...')
        start_time = time.time()
        test_vector = [0.1] * 384
        results = client.query_points(
            collection_name='documents',
            query=test_vector,
            limit=3
        )
        end_time = time.time()
        print(f'✅ Query took {end_time - start_time:.2f}s')
        print(f'   Retrieved {len(results.points)} results')
    
except Exception as e:
    print(f'❌ Error: {e}')
