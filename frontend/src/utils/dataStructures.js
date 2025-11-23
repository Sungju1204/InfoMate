/**
 * 자료구조 유틸리티 모듈
 * 해시 테이블, 그래프 등 자료구조 구현
 */

/**
 * 해시 테이블 (Hash Table)
 * 시간 복잡도: 평균 O(1) 조회/삽입/삭제, 최악 O(n)
 * 공간 복잡도: O(n)
 * 
 * 키-값 쌍을 저장하고 빠르게 조회할 수 있는 자료구조
 */
export class HashTable {
  constructor(size = 100) {
    // 해시 테이블의 크기
    this.size = size
    // 버킷 배열: 각 버킷은 키-값 쌍의 배열
    this.buckets = new Array(size).fill(null).map(() => [])
    // 저장된 항목의 개수
    this.count = 0
  }

  /**
   * 해시 함수 (Hash Function)
   * 문자열을 해시 테이블의 인덱스로 변환
   * 
   * @param {string} key - 해시할 키
   * @returns {number} 해시 인덱스
   */
  hash(key) {
    let hash = 0
    // 문자열의 각 문자를 순회하며 해시 값 계산
    for (let i = 0; i < key.length; i++) {
      // 문자 코드를 사용하여 해시 값 계산
      hash = (hash << 5) - hash + key.charCodeAt(i)
      // 32비트 정수로 변환
      hash = hash & hash
    }
    // 음수 방지 및 테이블 크기 내로 조정
    return Math.abs(hash) % this.size
  }

  /**
   * 값 삽입 (Insert)
   * 시간 복잡도: 평균 O(1)
   * 
   * @param {string} key - 키
   * @param {*} value - 값
   */
  set(key, value) {
    // 해시 인덱스 계산
    const index = this.hash(key)
    const bucket = this.buckets[index]

    // 같은 키가 이미 있는지 확인
    const existingIndex = bucket.findIndex(item => item.key === key)
    
    if (existingIndex !== -1) {
      // 기존 항목 업데이트
      bucket[existingIndex].value = value
    } else {
      // 새 항목 추가
      bucket.push({ key, value })
      this.count++
    }
  }

  /**
   * 값 조회 (Get)
   * 시간 복잡도: 평균 O(1)
   * 
   * @param {string} key - 키
   * @returns {*} 값 또는 undefined
   */
  get(key) {
    // 해시 인덱스 계산
    const index = this.hash(key)
    const bucket = this.buckets[index]

    // 버킷에서 키에 해당하는 항목 찾기
    const item = bucket.find(item => item.key === key)
    return item ? item.value : undefined
  }

  /**
   * 값 삭제 (Delete)
   * 시간 복잡도: 평균 O(1)
   * 
   * @param {string} key - 키
   * @returns {boolean} 삭제 성공 여부
   */
  delete(key) {
    // 해시 인덱스 계산
    const index = this.hash(key)
    const bucket = this.buckets[index]

    // 버킷에서 키에 해당하는 항목의 인덱스 찾기
    const itemIndex = bucket.findIndex(item => item.key === key)
    
    if (itemIndex !== -1) {
      // 항목 삭제
      bucket.splice(itemIndex, 1)
      this.count--
      return true
    }

    return false
  }

  /**
   * 키 존재 여부 확인
   * 시간 복잡도: 평균 O(1)
   * 
   * @param {string} key - 키
   * @returns {boolean} 키 존재 여부
   */
  has(key) {
    return this.get(key) !== undefined
  }

  /**
   * 모든 키 반환
   * 
   * @returns {Array} 키 배열
   */
  keys() {
    const keys = []
    // 모든 버킷을 순회하며 키 수집
    for (const bucket of this.buckets) {
      for (const item of bucket) {
        keys.push(item.key)
      }
    }
    return keys
  }

  /**
   * 모든 값 반환
   * 
   * @returns {Array} 값 배열
   */
  values() {
    const values = []
    // 모든 버킷을 순회하며 값 수집
    for (const bucket of this.buckets) {
      for (const item of bucket) {
        values.push(item.value)
      }
    }
    return values
  }

  /**
   * 해시 테이블이 비어있는지 확인
   * 
   * @returns {boolean} 비어있으면 true
   */
  isEmpty() {
    return this.count === 0
  }

  /**
   * 해시 테이블 크기 반환
   * 
   * @returns {number} 저장된 항목의 개수
   */
  size() {
    return this.count
  }
}

/**
 * 그래프 (Graph)
 * 시간 복잡도: 인접 리스트 표현 시 O(V + E) - V: 정점 수, E: 간선 수
 * 공간 복잡도: O(V + E)
 * 
 * 정점(Vertex)과 간선(Edge)으로 구성된 자료구조
 * 기사 간의 관계를 표현하는데 사용
 */
export class Graph {
  constructor() {
    // 인접 리스트: 각 정점에 연결된 정점들의 배열
    this.adjacencyList = new Map()
  }

  /**
   * 정점 추가
   * 
   * @param {*} vertex - 추가할 정점
   */
  addVertex(vertex) {
    // 정점이 없으면 빈 배열로 초기화
    if (!this.adjacencyList.has(vertex)) {
      this.adjacencyList.set(vertex, [])
    }
  }

  /**
   * 간선 추가 (무방향 그래프)
   * 
   * @param {*} vertex1 - 첫 번째 정점
   * @param {*} vertex2 - 두 번째 정점
   * @param {number} weight - 가중치 (선택적)
   */
  addEdge(vertex1, vertex2, weight = 1) {
    // 정점이 없으면 추가
    this.addVertex(vertex1)
    this.addVertex(vertex2)

    // 양방향 간선 추가
    this.adjacencyList.get(vertex1).push({ vertex: vertex2, weight })
    this.adjacencyList.get(vertex2).push({ vertex: vertex1, weight })
  }

  /**
   * 깊이 우선 탐색 (DFS - Depth First Search)
   * 시간 복잡도: O(V + E)
   * 공간 복잡도: O(V)
   * 
   * @param {*} startVertex - 시작 정점
   * @param {Function} callback - 각 정점을 방문할 때 호출할 함수
   * @returns {Array} 방문한 정점들의 배열
   */
  dfs(startVertex, callback = null) {
    // 방문한 정점을 추적하는 Set
    const visited = new Set()
    // 방문 순서를 저장하는 배열
    const result = []

    /**
     * 재귀적 DFS 함수
     * 
     * @param {*} vertex - 현재 정점
     */
    const dfsRecursive = (vertex) => {
      // 이미 방문한 정점이면 건너뛰기
      if (visited.has(vertex)) {
        return
      }

      // 정점 방문 처리
      visited.add(vertex)
      result.push(vertex)

      // 콜백 함수 호출
      if (callback) {
        callback(vertex)
      }

      // 인접한 정점들을 재귀적으로 방문
      const neighbors = this.adjacencyList.get(vertex) || []
      for (const neighbor of neighbors) {
        dfsRecursive(neighbor.vertex)
      }
    }

    // DFS 시작
    dfsRecursive(startVertex)
    return result
  }

  /**
   * 너비 우선 탐색 (BFS - Breadth First Search)
   * 시간 복잡도: O(V + E)
   * 공간 복잡도: O(V)
   * 
   * @param {*} startVertex - 시작 정점
   * @param {Function} callback - 각 정점을 방문할 때 호출할 함수
   * @returns {Array} 방문한 정점들의 배열
   */
  bfs(startVertex, callback = null) {
    // 방문한 정점을 추적하는 Set
    const visited = new Set()
    // 방문 순서를 저장하는 배열
    const result = []
    // 큐: BFS에서 사용하는 자료구조 (FIFO)
    const queue = [startVertex]
    visited.add(startVertex)

    // 큐가 빌 때까지 반복
    while (queue.length > 0) {
      // 큐에서 정점 꺼내기 (FIFO)
      const vertex = queue.shift()
      result.push(vertex)

      // 콜백 함수 호출
      if (callback) {
        callback(vertex)
      }

      // 인접한 정점들을 큐에 추가
      const neighbors = this.adjacencyList.get(vertex) || []
      for (const neighbor of neighbors) {
        if (!visited.has(neighbor.vertex)) {
          visited.add(neighbor.vertex)
          queue.push(neighbor.vertex)
        }
      }
    }

    return result
  }

  /**
   * 특정 정점과 연결된 모든 정점 찾기 (DFS 사용)
   * 
   * @param {*} startVertex - 시작 정점
   * @param {number} maxDepth - 최대 탐색 깊이
   * @returns {Array} 연결된 정점들의 배열
   */
  getConnectedVertices(startVertex, maxDepth = 3) {
    const connected = []
    const visited = new Set()

    /**
     * 재귀적 DFS 함수 (깊이 제한)
     * 
     * @param {*} vertex - 현재 정점
     * @param {number} depth - 현재 깊이
     */
    const dfsRecursive = (vertex, depth = 0) => {
      // 최대 깊이를 초과하면 중단
      if (depth > maxDepth) {
        return
      }

      // 이미 방문한 정점이면 건너뛰기
      if (visited.has(vertex)) {
        return
      }

      // 시작 정점이 아니면 결과에 추가
      if (depth > 0) {
        connected.push(vertex)
      }

      // 정점 방문 처리
      visited.add(vertex)

      // 인접한 정점들을 재귀적으로 방문
      const neighbors = this.adjacencyList.get(vertex) || []
      for (const neighbor of neighbors) {
        dfsRecursive(neighbor.vertex, depth + 1)
      }
    }

    // DFS 시작
    dfsRecursive(startVertex)
    return connected
  }

  /**
   * 그래프의 모든 정점 반환
   * 
   * @returns {Array} 정점 배열
   */
  getVertices() {
    return Array.from(this.adjacencyList.keys())
  }

  /**
   * 특정 정점의 인접 정점들 반환
   * 
   * @param {*} vertex - 정점
   * @returns {Array} 인접 정점들의 배열
   */
  getNeighbors(vertex) {
    return this.adjacencyList.get(vertex) || []
  }
}

