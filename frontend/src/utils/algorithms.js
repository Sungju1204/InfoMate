/**
 * 알고리즘 유틸리티 모듈
 * 정렬 및 탐색 알고리즘 구현
 */

/**
 * 퀵 정렬 (Quick Sort)
 * 시간 복잡도: 평균 O(n log n), 최악 O(n²)
 * 공간 복잡도: O(log n)
 * 
 * @param {Array} arr - 정렬할 배열
 * @param {Function} compareFn - 비교 함수 (선택적)
 * @returns {Array} 정렬된 배열
 */
export function quickSort(arr, compareFn = (a, b) => a - b) {
  // 베이스 케이스: 배열 길이가 1 이하면 이미 정렬된 상태
  if (arr.length <= 1) {
    return arr
  }

  // 피벗 선택: 배열의 중간 요소를 피벗으로 선택
  const pivotIndex = Math.floor(arr.length / 2)
  const pivot = arr[pivotIndex]

  // 피벗보다 작은 요소들
  const left = []
  // 피벗보다 큰 요소들
  const right = []
  // 피벗과 같은 요소들
  const equal = []

  // 배열을 순회하며 피벗과 비교하여 분류
  for (let i = 0; i < arr.length; i++) {
    const comparison = compareFn(arr[i], pivot)
    if (comparison < 0) {
      left.push(arr[i])
    } else if (comparison > 0) {
      right.push(arr[i])
    } else {
      equal.push(arr[i])
    }
  }

  // 재귀적으로 왼쪽과 오른쪽을 정렬하고 합치기
  return [...quickSort(left, compareFn), ...equal, ...quickSort(right, compareFn)]
}

/**
 * 병합 정렬 (Merge Sort)
 * 시간 복잡도: O(n log n) - 항상 일정
 * 공간 복잡도: O(n)
 * 
 * @param {Array} arr - 정렬할 배열
 * @param {Function} compareFn - 비교 함수 (선택적)
 * @returns {Array} 정렬된 배열
 */
export function mergeSort(arr, compareFn = (a, b) => a - b) {
  // 베이스 케이스: 배열 길이가 1 이하면 이미 정렬된 상태
  if (arr.length <= 1) {
    return arr
  }

  // 배열을 반으로 나누기
  const mid = Math.floor(arr.length / 2)
  const left = arr.slice(0, mid)
  const right = arr.slice(mid)

  // 재귀적으로 왼쪽과 오른쪽을 정렬
  const sortedLeft = mergeSort(left, compareFn)
  const sortedRight = mergeSort(right, compareFn)

  // 정렬된 두 배열을 병합
  return merge(sortedLeft, sortedRight, compareFn)
}

/**
 * 병합 함수 (Merge)
 * 두 개의 정렬된 배열을 하나로 병합
 * 
 * @param {Array} left - 정렬된 왼쪽 배열
 * @param {Array} right - 정렬된 오른쪽 배열
 * @param {Function} compareFn - 비교 함수
 * @returns {Array} 병합된 정렬된 배열
 */
function merge(left, right, compareFn) {
  const result = []
  let leftIndex = 0
  let rightIndex = 0

  // 두 배열의 요소를 비교하며 작은 것부터 결과 배열에 추가
  while (leftIndex < left.length && rightIndex < right.length) {
    if (compareFn(left[leftIndex], right[rightIndex]) <= 0) {
      result.push(left[leftIndex])
      leftIndex++
    } else {
      result.push(right[rightIndex])
      rightIndex++
    }
  }

  // 남은 요소들을 결과 배열에 추가
  return result.concat(left.slice(leftIndex)).concat(right.slice(rightIndex))
}

/**
 * 이진 탐색 (Binary Search)
 * 시간 복잡도: O(log n)
 * 공간 복잡도: O(1)
 * 
 * 전제 조건: 배열이 정렬되어 있어야 함
 * 
 * @param {Array} arr - 정렬된 배열
 * @param {*} target - 찾을 값
 * @param {Function} compareFn - 비교 함수 (선택적)
 * @returns {number} 찾은 경우 인덱스, 못 찾은 경우 -1
 */
export function binarySearch(arr, target, compareFn = (a, b) => a - b) {
  let left = 0
  let right = arr.length - 1

  // left가 right보다 작거나 같은 동안 반복
  while (left <= right) {
    // 중간 인덱스 계산
    const mid = Math.floor((left + right) / 2)
    const comparison = compareFn(arr[mid], target)

    // 찾은 경우
    if (comparison === 0) {
      return mid
    }
    // 중간 값이 목표보다 큰 경우: 왼쪽 절반 탐색
    else if (comparison > 0) {
      right = mid - 1
    }
    // 중간 값이 목표보다 작은 경우: 오른쪽 절반 탐색
    else {
      left = mid + 1
    }
  }

  // 찾지 못한 경우
  return -1
}

/**
 * 선형 탐색 (Linear Search)
 * 시간 복잡도: O(n)
 * 공간 복잡도: O(1)
 * 
 * @param {Array} arr - 탐색할 배열
 * @param {*} target - 찾을 값
 * @param {Function} compareFn - 비교 함수 (선택적)
 * @returns {number} 찾은 경우 인덱스, 못 찾은 경우 -1
 */
export function linearSearch(arr, target, compareFn = (a, b) => a === b) {
  // 배열을 처음부터 끝까지 순회
  for (let i = 0; i < arr.length; i++) {
    // 찾은 경우 인덱스 반환
    if (compareFn(arr[i], target)) {
      return i
    }
  }

  // 찾지 못한 경우
  return -1
}

/**
 * 문자열 매칭 (String Matching)
 * 시간 복잡도: O(n * m) - n: 텍스트 길이, m: 패턴 길이
 * 공간 복잡도: O(1)
 * 
 * @param {string} text - 검색할 텍스트
 * @param {string} pattern - 찾을 패턴
 * @returns {boolean} 패턴이 텍스트에 포함되어 있는지 여부
 */
export function stringMatch(text, pattern) {
  const textLength = text.length
  const patternLength = pattern.length

  // 패턴이 텍스트보다 길면 찾을 수 없음
  if (patternLength > textLength) {
    return false
  }

  // 텍스트를 순회하며 패턴과 비교
  for (let i = 0; i <= textLength - patternLength; i++) {
    let match = true

    // 패턴의 각 문자를 비교
    for (let j = 0; j < patternLength; j++) {
      if (text[i + j].toLowerCase() !== pattern[j].toLowerCase()) {
        match = false
        break
      }
    }

    // 모든 문자가 일치하면 찾음
    if (match) {
      return true
    }
  }

  return false
}

/**
 * 키워드 추출 (Keyword Extraction)
 * 텍스트에서 키워드를 추출하는 간단한 알고리즘
 * 
 * @param {string} text - 키워드를 추출할 텍스트
 * @param {number} minLength - 최소 키워드 길이
 * @returns {Array} 추출된 키워드 배열
 */
export function extractKeywords(text, minLength = 2) {
  // 특수문자 제거 및 소문자 변환
  const cleaned = text.replace(/[^\w\s가-힣]/g, ' ').toLowerCase()
  
  // 공백으로 분리
  const words = cleaned.split(/\s+/)
  
  // 빈 문자열 제거 및 최소 길이 필터링
  const keywords = words.filter(word => word.length >= minLength)
  
  // 중복 제거
  const uniqueKeywords = [...new Set(keywords)]
  
  return uniqueKeywords
}

