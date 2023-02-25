# this file is meant to pre process the data and structure them in the correct format
# that is easily alignable

using RData
using LinearAlgebra
using MultivariateStats
using HDF5
using ArgParse


function parse_commandline()
  s = ArgParseSettings()

  @add_arg_table s begin
      "--data_dir"
          arg_type = String
          default = "./data"
  end

  return parse_args(s)
end

parsed_args = parse_commandline()

data_dir = parsed_args["data_dir"]
input_file = data_dir * "/raw/preeclampsia.rda"
output_file = data_dir * "/processed/preeclampsia.h5"

E = load(input_file)

# cytof
fparse(t) = parse(Int,t[9:10]) < 14 ? 1 : parse(Int,t[9:10]) < 28 ? 2 : 3

#### 1.
s = String.(names(E["metabolome_plasma_dataFINAL"])[1:end-14])
subjects_plasma = parse.(Int,map(i->s[i][2:6],1:length(s)))
terms_plasma = fparse.(s)

#### 2.
subjects_somalogic = E["somalogic_dataFINAL"][:,:Subject_ID];
terms_somalogic = Vector{Int}(undef,size(E["somalogic_dataFINAL"],1));
terms_somalogic[findall(E["somalogic_dataFINAL"][:,:TimePoint].=="1st Tri")] .= 1
terms_somalogic[findall(E["somalogic_dataFINAL"][:,:TimePoint].=="2nd Tri")] .= 2
terms_somalogic[findall(E["somalogic_dataFINAL"][:,:TimePoint].=="3rd Tri")] .= 3

#### 3.
subjects_microbiome = E["microbiome_dataFINAL"][:,:individual];
terms_microbiome = E["microbiome_dataFINAL"][:,:trimester]

#### 4.
subjects_immune = E["immune_dataFINAL"][:,:individual];
terms_immune = E["immune_dataFINAL"][:,:trimester]

#### 5.
s = String.(names(E["cfrna_dataFINAL"]))
subjects_cfrna = parse.(Int,map(i->s[i][2:6],3:length(s)))
terms_cfrna = fparse.(s[3:end])

#### 6.
s = String.(names(E["lipidome_dataFINAL"]))
subjects_lipidome = parse.(Int,map(i->s[i][2:6],2:length(s)))
terms_lipidome = fparse.(s[2:end])

#### 7.
s = String.(names(E["metabolome_urine_dataFINAL"])[1:end-14])
subjects_urine = parse.(Int,map(i->s[i][2:6],1:length(s)))
terms_urine = fparse.(s)

subjects = intersect(subjects_plasma,
                    subjects_somalogic,
                    subjects_microbiome,
                    subjects_immune, # if I remove this I get a new set with 35 subjects
                    subjects_cfrna,
                    subjects_lipidome,
                    subjects_urine)

#### 1.
E_plasma = E["metabolome_plasma_dataFINAL"][:,findall((in)(subjects), subjects_plasma)]
subjects_plasma_smaller = subjects_plasma[findall((in)(subjects), subjects_plasma)]
terms_plasma_smaller = terms_plasma[findall((in)(subjects), subjects_plasma)]

#### 2.
E_somalogic = E["somalogic_dataFINAL"][findall((in)(subjects), subjects_somalogic),:]
subjects_somalogic_smaller = subjects_somalogic[findall((in)(subjects), subjects_somalogic)]
terms_somalogic_smaller = terms_somalogic[findall((in)(subjects), subjects_somalogic)]

#### 3.
E_microbiome = E["microbiome_dataFINAL"][findall((in)(subjects), subjects_microbiome),:]
subjects_microbiome_smaller = subjects_microbiome[findall((in)(subjects), subjects_microbiome)]
terms_microbiome_smaller = terms_microbiome[findall((in)(subjects), subjects_microbiome)]

#### 4.
E_immune = E["immune_dataFINAL"][findall((in)(subjects), subjects_immune),:]
subjects_immune_smaller = subjects_immune[findall((in)(subjects), subjects_immune)]
terms_immune_smaller = terms_immune[findall((in)(subjects), subjects_immune)]

#### 5.
E_cfrna = E["cfrna_dataFINAL"][:,2 .+ findall((in)(subjects), subjects_cfrna)]
subjects_cfrna_smaller = subjects_cfrna[findall((in)(subjects), subjects_cfrna)]
terms_cfrna_smaller = terms_cfrna[findall((in)(subjects), subjects_cfrna)]

#### 6.
E_lipidome = E["lipidome_dataFINAL"][:,1 .+ findall((in)(subjects), subjects_lipidome)]
subjects_lipidome_smaller = subjects_lipidome[findall((in)(subjects), subjects_lipidome)]
terms_lipidome_smaller = terms_lipidome[findall((in)(subjects), subjects_lipidome)]

#### 7.
E_urine = E["metabolome_urine_dataFINAL"][:,findall((in)(subjects), subjects_urine)]
subjects_urine_smaller = subjects_urine[findall((in)(subjects), subjects_urine)]
terms_urine_smaller = terms_urine[findall((in)(subjects), subjects_urine)]

# names are
# plasma,somalogic,microbiome,immune,cfrna,lipidome,urine
# E_ : dataset
# subjects_XYZ
# terms_XYZ

align_plasma = []
align_somalogic = []
align_microbiome = []
align_immune = []
align_cfrna = []
align_lipidome = []
align_urine = []

for (i,sid) in enumerate(subjects)

  is1 = findall(subjects_plasma_smaller.==sid)
  is2 = findall(subjects_somalogic_smaller.==sid)
  is3 = findall(subjects_microbiome_smaller.==sid)
  is4 = findall(subjects_immune_smaller.==sid)
  is5 = findall(subjects_cfrna_smaller.==sid)
  is6 = findall(subjects_lipidome_smaller.==sid)
  is7 = findall(subjects_urine_smaller.==sid)

  toconsider = min(length(is1),length(is2),length(is3))
  trimesters_to_include = intersect(terms_plasma_smaller[is1],
                    terms_somalogic_smaller[is2],
                    terms_microbiome_smaller[is3],
                    terms_immune_smaller[is4],
                    terms_cfrna_smaller[is5],
                    terms_lipidome_smaller[is6],
                    terms_urine_smaller[is7])

  for (j,ti) in enumerate(trimesters_to_include)
    push!(align_plasma,is1[findlast(terms_plasma_smaller[is1].==ti)])
    push!(align_somalogic,is2[findlast(terms_somalogic_smaller[is2].==ti)])
    push!(align_microbiome,is3[findlast(terms_microbiome_smaller[is3].==ti)])
    push!(align_immune,is4[findlast(terms_immune_smaller[is4].==ti)])
    push!(align_cfrna,is5[findlast(terms_cfrna_smaller[is5].==ti)])
    push!(align_lipidome,is6[findlast(terms_lipidome_smaller[is6].==ti)])
    push!(align_urine,is7[findlast(terms_urine_smaller[is7].==ti)])
  end
end

####### now align the data and drop the features that have missings in them.

#### 1.
E_plasma_aligned = copy(Matrix(E_plasma[:,align_plasma])')
E_plasma_aligned = E_plasma_aligned[:,findall(sum(E_plasma_aligned.==0,dims=1)[:].==0)]
#### 2.
E_somalogic_aligned = Matrix(E_somalogic[align_somalogic,5:end])
E_somalogic_aligned = E_somalogic_aligned[:,findall(sum(E_somalogic_aligned.==0,dims=1)[:].==0)]

#### 3.
E_microbiome_aligned = Matrix(E_microbiome[align_microbiome,30:end])
# E_microbiome_aligned = E_microbiome_aligned[:,findall(sum(E_microbiome_aligned.==0,dims=1)[:].==0)]

#### 4.
E_immune_aligned = Matrix(E_immune[align_immune,7:end])
idsimm = findall(sum(ismissing.(E_immune_aligned),dims=1)[:].==0)
E_immune_aligned = Float64.(E_immune_aligned[:,idsimm])
E_immune_aligned = E_immune_aligned[:,findall(sum(E_immune_aligned.==0,dims=1)[:].==0)]

#### 5.
E_cfrna_aligned = copy(Matrix(E_cfrna[:,align_cfrna])')
E_cfrna_aligned = E_cfrna_aligned[:,findall(sum(E_cfrna_aligned.==0,dims=1)[:].==0)]

#### 6.
E_lipidome_aligned = copy(Matrix(E_lipidome[:,align_cfrna])')
E_lipidome_aligned = E_lipidome_aligned[:,findall(sum(E_lipidome_aligned.==0,dims=1)[:].==0)]

#### 7.
E_urine_aligned = copy(Matrix(E_urine[:,align_urine])')
E_urine_aligned = E_urine_aligned[:,findall(sum(E_urine_aligned.==0,dims=1)[:].==0)]

pre_ids_ref = findall(E_immune[align_immune,:sample_type].=="PreE")
ctrl_ids_ref = findall(E_immune[align_immune,:sample_type].=="Ctrl")

####### Create vector of aligned arrays, normalize, then save for future use
alignedArrays = [E_plasma_aligned, E_somalogic_aligned, E_microbiome_aligned,
                E_immune_aligned, E_cfrna_aligned, E_lipidome_aligned,
                E_urine_aligned]

refAlignedArrays = deepcopy(alignedArrays)

arrayLabels = ["E_plasma_aligned", "E_somalogic_aligned", "E_microbiome_aligned",
                "E_immune_aligned", "E_cfrna_aligned", "E_lipidome_aligned",
                "E_urine_aligned"]

# normalizedAlignedArrays = Vector{Array{Float64, 2}}()
# for i in 1:length(alignedArrays)
#   push!(normalizedAlignedArrays, centeredNormalizedMatrix(alignedArrays[i]))
# end

# save("data/alignedArrays.jld", "alignedUnnormalized", alignedArrays, "alignedNormalized", normalizedAlignedArrays)

Ur = hcat(
    refAlignedArrays[1],
    refAlignedArrays[2],
    refAlignedArrays[3],
    refAlignedArrays[4],
    refAlignedArrays[5],
    refAlignedArrays[6],
    refAlignedArrays[7])

if isfile(output_file)
    rm(output_file)
end
h5open(output_file, "cw") do file
    write(file, "data", Array(Ur'))
    write(file, "rownames", [1:size(Ur, 1);])
    write(file, "colnames", [1:size(Ur, 2);])
end